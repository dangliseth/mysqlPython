from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort
import datetime

from fpdf import FPDF

from invemp.auth import login_required, admin_required
from invemp.db import get_cursor

bp = Blueprint('dashboard', __name__)


@bp.route('/', defaults={'table_name': 'items'})
@bp.route('/<table_name>')
@login_required
def index(table_name):
    # check for admin access
    if g.user[3] != 'admin' and table_name != 'items':
        flash("You do not have permission to access this table.")
        return redirect(url_for('dashboard.index', table_name))
    

    c = get_cursor()
    if table_name == 'items':
        query = """
            SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
            i.comment, e.name AS 'Assigned To', i.department, i.last_updated
            FROM items i
            LEFT JOIN employees e ON i.employee = e.employee_id
            LIMIT 100
        """
        c.execute(query)
        items = c.fetchall()
        columns = [column[0] for column in c.description]
    elif table_name == 'user_accounts':
        c.execute(f"SELECT id, username, account_type FROM `{table_name}` LIMIT 100")
        columns = [column[0] for column in c.description if column != 'password']
        items = c.fetchall()
    else:
        # Generic query for other tables
        c.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        items = c.fetchall()
        columns = [column[0] for column in c.description]
    c.close()

    tables = get_tables()
    filters = {}
    return render_template('dashboard/index.html', items=items, columns=columns, 
                           table_name=table_name, tables=tables, filters = filters)

def get_tables():
    c = get_cursor()
    c.execute("SHOW TABLES")
    tables = [row[0] for row in c.fetchall()]
    c.close()
    return tables

def get_entry(entry_id, table_name):
    c = get_cursor()

    # Get the column names for the table
    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]

    # Identify the primary key column (id, ends with _id, or ID)
    id_column = None
    for column in columns:
        if column.lower() == 'id' or column.endswith('_id') or column == 'ID':
            id_column = column
            break

    # Fetch the entry based on the primary key column
    query = f"SELECT * FROM `{table_name}` WHERE `{id_column}` = %s"
    c.execute(query, (entry_id,))
    entry = c.fetchone()
    c.close()

    return entry

def get_employees():
    c = get_cursor()
    all_employees = c.execute(f"SELECT * FROM employees")
    return all_employees

def get_dropdown_options():
    dropdown_options = {
        'category': ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5', 'Category 6'],
        'department': ['Registrar', 'SGS', 'SOB', 'SCJ', 'SOA', 'SOE', 'SOL', 'Administration', 'OSA', 'SESO',
                       'Accounting', 'HR', 'Cashier', 'OTP', 'Marketing', 'SHS', 'Quacro', 'Library']
    }
    return dropdown_options

@bp.route('/<table_name>/create', methods=('GET', 'POST'))
@admin_required
def create(table_name):
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()

    filters = {}

    dropdown_options = get_dropdown_options()

    id_column = None
    for column in columns:
        if column == 'id' or column.endswith('_id'):
            id_column = column
            break

    if request.method == 'POST':
        if id_column:
            c = get_cursor()
            c.execute(f"SELECT MAX({id_column}) FROM `{table_name}`")
            max_id = c.fetchone()[0]
            next_id = (max_id or 0) + 1  # Increment the max ID or start from 1
            c.close()
        else:
            next_id = None

        # Prepare values for insertion
        values = []
        current_datetime = datetime.datetime.now()
        for column in columns:
            if column == id_column:
                values.append(next_id)
            elif column == 'last_updated':
                values.append(current_datetime)
            else:
                values.append(request.form.get(column))

        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"

        c = get_cursor()
        c.execute(query, values)
        c.connection.commit()
        c.close()

        flash(f"Successfully created new {table_name[:-1]}")
        return redirect(url_for('dashboard.view_table', table_name=table_name))
    return render_template('dashboard/create.html', table_name=table_name, 
                           columns=columns, dropdown_options=dropdown_options, filters = filters)

@bp.route('/<table_name>/<id>/update', methods=('GET', 'POST'))
@admin_required
def update(id, table_name):
    entry = get_entry(id, table_name)
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()

    dropdown_options = get_dropdown_options()
    current_datetime = datetime.datetime.now()

    filters = {}

    if request.method == 'POST':
        values = []
        update_columns = []
        for column in columns:
            if column == 'id' or column.endswith('_id') or column == 'ID':  # Skip ID columns
                id_column = column
                continue
            ##if column == 'employee':

            if column == 'last_updated':
                values.append(current_datetime)
                update_columns.append(column)
            else:
                values.append(request.form.get(column))
                update_columns.append(column)

        placeholders = ', '.join([f"`{col}` = %s" for col in update_columns])
        query = f"UPDATE `{table_name}` SET {placeholders} WHERE `{id_column}` = %s"
        values.append(id)

        c = get_cursor()
        c.execute(query, values)
        c.connection.commit()
        c.close()

        flash(f"Successfully updated {table_name[:-1]}")
        return redirect(url_for('dashboard.index', table_name=table_name))
    return render_template('dashboard/update.html', entry=entry, table_name=table_name, 
                           columns=columns, dropdown_options=dropdown_options, filters = filters)

@bp.route('/<table_name>/filter', methods=('GET', 'POST'))
@login_required
def filter_items(table_name):
    c = get_cursor()

    # Fetch the column names for the table
    if table_name == 'items':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                   'comment', 'Assigned To', 'department', 'last_updated']
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]

    # Get filter criteria from the request
    filters = {column: request.args.get(column) for column in columns if request.args.get(column)}

    # Build the WHERE clause dynamically
    where_clauses = []
    filter_values = []
    for col, value in filters.items():
        if col == "Assigned To":
            where_clauses.append("e.name LIKE %s")
        else:
            where_clauses.append(f"i.`{col}` LIKE %s" if table_name == 'items' or table_name == 'items_disposal' else f"`{col}` LIKE %s")
        filter_values.append(f"%{value}%")
    where_clause = " AND ".join(where_clauses)
    if table_name == 'items' or table_name == 'items_disposal':
        sql_query = f"""
            SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
            i.comment, e.name AS 'Assigned To', i.department, i.last_updated
            FROM items i
            LEFT JOIN employees e ON i.employee = e.employee_id
        """
    else:
        sql_query = f"SELECT * FROM `{table_name}`"
    if where_clause:
        sql_query += f" WHERE {where_clause}"
    sql_query += " LIMIT 100"

    filter_values = [f"%{value}%" for value in filters.values()]

    # Execute the query with filter values
    c.execute(sql_query, tuple(filter_values))
    items = c.fetchall()
    c.close()

    tables = get_tables()
    return render_template('dashboard/index.html', items=items, columns=columns, table_name=table_name, tables=tables, filters=filters)

@bp.route('/<table_name>/convert_pdf')
@login_required
def convert_pdf(table_name):
    c = get_cursor()

    # Fetch the column names for the table
    if table_name == 'items':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                    'comment', 'Assigned To', 'department', 'last_updated']
        base_query = """
            SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
            i.comment, e.name AS 'Assigned To', i.department, i.last_updated
            FROM items i
            LEFT JOIN employees e ON i.employee = e.employee_id
        """
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]
        base_query = f"SELECT * FROM `{table_name}`"

    # --- Handle Filters ---
    filters = {column: request.args.get(column) for column in columns if request.args.get(column)}
    where_clauses = []
    filter_values = []
    for col, value in filters.items():
        if table_name == 'items' and col == "Assigned To":
            where_clauses.append("e.name LIKE %s")
        elif table_name == 'items':
            where_clauses.append(f"i.`{col}` LIKE %s")
        else:
            where_clauses.append(f"`{col}` LIKE %s")
        filter_values.append(f"%{value}%")
    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    # --- Handle Sorting ---
    sort_column = request.args.get('column')
    sort_direction = request.args.get('direction', 'asc')
    order_sql = ""
    if sort_column and sort_column in columns and sort_direction in ['asc', 'desc']:
        # For items, prefix with i. unless it's 'Assigned To'
        if table_name == 'items':
            if sort_column == "Assigned To":
                order_sql = f" ORDER BY e.name {sort_direction}"
            else:
                order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            order_sql = f" ORDER BY `{sort_column}` {sort_direction}"

    # --- Final Query ---
    sql_query = base_query + where_sql + order_sql

    # Execute the query
    c.execute(sql_query, tuple(filter_values))
    items = c.fetchall()
    c.close()

    # Generate PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add table name as title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"{table_name.capitalize()} Report", ln=True, align='C')
    pdf.ln(10)

    # Add column headers
    pdf.set_font("Arial", style="B", size=12)
    for column in columns:
        pdf.cell(40, 10, column, border=1, align='C')
    pdf.ln()

    # Add rows
    pdf.set_font("Arial", size=10)
    for item in items:
        for value in item:
            pdf.cell(40, 10, str(value), border=1, align='C')
        pdf.ln()

    # Output PDF as a downloadable file
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={table_name}_report.pdf'
    return response