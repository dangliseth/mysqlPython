from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort
import datetime

import io
import qrcode
from fpdf import FPDF
from weasyprint import CSS, HTML

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
    filters = get_filters(table_name)
    return render_template('dashboard/index.html', items=items, columns=columns, 
                           table_name=table_name, tables=tables, filters = filters, is_index = True)

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


def get_dropdown_options():
    c = get_cursor()
    
    # Get all employees
    c.execute("SELECT employee_id, name FROM employees")
    employees = c.fetchall()
    
    # Format as list of "ID - Name" strings
    employee_options = [f"{emp[1]}" for emp in employees]

    dropdown_options = {
        'category': ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5', 'Category 6'],
        'department': ['Registrar', 'SGS', 'SOB', 'SCJ', 'SOA', 'SOE', 'SOL', 'Administration', 'OSA', 'SESO',
                       'Accounting', 'HR', 'Cashier', 'OTP', 'Marketing', 'SHS', 'Quacro', 'Library'],
        'Assigned To': employee_options,
        'account_type': ['user', 'admin']
    }
    c.close()
    return dropdown_options

@bp.route('/<table_name>/create', methods=('GET', 'POST'))
@admin_required
def create(table_name):
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    if table_name == 'items' or table_name == 'items_disposal':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                   'comment', 'Assigned To', 'department', 'last_updated']
    else:
        columns = [row[0] for row in c.fetchall()]
    c.close()

    filters = get_filters(table_name)

    dropdown_options = get_dropdown_options()
    
    id_column = None
    for column in columns:
        if column == 'id' or column.endswith('_id'):
            id_column = column
            break

    # Max id check
    if table_name == 'items':
        table_name2 = 'items_disposal'
    elif table_name == 'employees':
        table_name2 = 'employees_archive'
    else:
        table_name2 = None
    if request.method == 'POST':
        if id_column:
            c = get_cursor()
            if table_name2:
                c.execute(f"""
                    SELECT MAX({id_column}) AS max_id
                    FROM (
                        SELECT `{id_column}` FROM `{table_name}`
                        UNION ALL
                        SELECT `{id_column}` FROM `{table_name2}`
                    ) AS combined_ids
                """)
            else:
                c.execute(f"SELECT MAX({id_column}) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            if isinstance(max_id, str) and max_id.startswith('MLQU-'):
                # Extract numeric part, increment, and format with leading zeros
                num_part = max_id.split('-')[-1]
                next_num = int(num_part) + 1 if num_part.isdigit() else 1
                next_id = f"MLQU-{next_num:07d}"
            else:
                try:
                    next_id = (int(max_id) if max_id is not None else 0) + 1
                except Exception:
                    next_id = 1
            c.close()
        else:
            next_id = None

        # Prepare values for insertion
        values = []
        current_datetime = datetime.datetime.now()
        insert_columns = []
        for column in columns:
            if column == id_column:
                values.append(next_id)
                insert_columns.append(column)
            elif column == 'last_updated':
                values.append(current_datetime)
                insert_columns.append(column)
            elif column == 'Assigned To':
                # Convert employee name to employee_id before inserting
                employee_name = request.form.get('Assigned To')
                if employee_name:
                    c_lookup = get_cursor()
                    c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (employee_name,))
                    emp_row = c_lookup.fetchone()
                    c_lookup.close()
                    employee_id = emp_row[0] if emp_row else None
                else:
                    employee_id = None
                values.append(employee_id)
                insert_columns.append('employee')
            else:
                values.append(request.form.get(column))
                insert_columns.append(column)

        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO `{table_name}` ({', '.join(insert_columns)}) VALUES ({placeholders})"


        c = get_cursor()
        c.execute(query, values)
        c.connection.commit()
        c.close()

        flash(f"Successfully created new {table_name[:-1]}")
        return redirect(url_for('dashboard.index', table_name=table_name, filters = filters))
    return render_template('dashboard/create.html', table_name=table_name, 
                           columns=columns, dropdown_options=dropdown_options, filters = filters)

@bp.route('/<table_name>/<id>/update', methods=('GET', 'POST'))
@admin_required
def update(id, table_name):
    entry = get_entry(id, table_name)
    entry = list(entry)
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    if table_name == 'items' or table_name == 'items_disposal':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                   'comment', 'Assigned To', 'department', 'last_updated']
    else:
        columns = [row[0] for row in c.fetchall()]
    c.close()

    dropdown_options = get_dropdown_options()
    current_datetime = datetime.datetime.now()

    filters = get_filters(table_name)

    if 'Assigned To' in columns:
        # Get the index of the employee column in the original data
        employee_idx = [i for i, col in enumerate(columns) if col == 'Assigned To'][0]
        
        # Get the employee_id from the entry
        employee_id = entry[employee_idx]
        
        if employee_id:  # Only query if employee_id exists
            c = get_cursor()
            try:
                c.execute("SELECT name FROM employees WHERE employee_id = %s", (employee_id,))
                result = c.fetchone()
                employee_name = result[0] if result else None
                entry[employee_idx] = employee_name  # Replace ID with name
            finally:
                c.close()
        else:
            entry[employee_idx] = None  # Ensure None is preserved

    if request.method == 'POST':
        values = []
        update_columns = []
        for column in columns:
            if column == 'id' or column.endswith('_id') or column == 'ID':  # Skip ID columns
                id_column = column
                continue
            if column == 'Assigned To':
                column = 'employee'
            elif column == 'last_updated':
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
    return render_template('dashboard/update.html', entry=entry, table_name=table_name, columns=columns, 
                           dropdown_options=dropdown_options, filters = filters)

@bp.route('/<table_name>/<id>/archive_scrap', methods=('GET', 'POST'))
@admin_required
def archive_scrap(id, table_name):
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()

    for column in columns:
        if column == 'id' or column.endswith('_id') or column == 'ID':  # Determin id column
            id_column = column
            break

    if request.method == 'POST':
        try:
            c = get_cursor()
            if table_name == 'items':
                # Move to items_disposal
                move_query = f"INSERT INTO items_disposal SELECT * FROM `{table_name}` WHERE `{id_column}` = %s"
                c.execute(move_query, (id,))
                delete_query = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
                c.execute(delete_query, (id,))
            else:
                # Move to employees_archive
                move_query = f"INSERT INTO employees_archive SELECT * FROM `{table_name}` WHERE `{id_column}` = %s"
                c.execute(move_query, (id,))
                delete_query = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
                c.execute(delete_query, (id,))
            c.connection.commit()
            flash("Entry archived successfully.")
        except Exception as e:
            c.connection.rollback()
            flash(f"Error archiving entry: {e}")
        finally:
            c.close()
    return redirect(url_for('dashboard.index', table_name = table_name))

@bp.route('/<table_name>/<id>/delete', methods=('GET', 'POST'))
def delete(id, table_name):
    c = get_cursor()
    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()

    for column in columns:
        if column == 'id' or column.endswith('_id') or column == 'ID':  # Determin id column
            id_column = column
            break

    if request.method == 'POST':
        c = get_cursor()
        delete_query = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
        c.execute(delete_query, (id,)) 
        c.connection.commit()
        flash(f"{id_column}: {id} DELETED from {table_name}")

    filters = get_filters(table_name)
    
    return redirect(url_for('dashboard.index', table_name = table_name, filters = filters))


@bp.route('/<table_name>/filter', methods=('GET', 'POST'))
@login_required
def filter_items(table_name):
    c = get_cursor()

    # Fetch the column names for the table
    if table_name == 'items' or table_name == 'items_disposal':
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
    return render_template('dashboard/index.html', items=items, columns=columns, table_name=table_name, 
                           tables=tables, filters=filters, is_index = True)

def get_filters(table_name):
    c = get_cursor()

    # Fetch the column names for the table
    if table_name == 'items':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                   'comment', 'Assigned To', 'department', 'last_updated']
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]

    filters = {column: request.args.get(column) for column in columns if request.args.get(column)}
    return filters

def calculate_column_widths(items, columns):
    """Calculate relative column widths based on content"""
    if not items:
        return {col: 1 for col in columns}
    
    # Sample first 10 rows to determine content length
    sample_rows = items[:10]
    width_factors = {}
    
    for col_idx, column in enumerate(columns):
        max_len = len(column)  # Start with header length
        for row in sample_rows:
            value = str(row[col_idx] if row[col_idx] is not None else '')
            max_len = max(max_len, len(value))
        
        # Special handling for known types
        if max_len > 50:
            width_factors[column] = 3
        elif max_len > 20:
            width_factors[column] = 2
        else:
            width_factors[column] = 0.5
    
    return width_factors

@bp.route('/<table_name>/convert_pdf')
@login_required
def convert_pdf(table_name):
    c = get_cursor()
    request_args = request.args.to_dict()


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
    where_clauses = []
    filter_values = []
    
    # Process each possible filter parameter
    for column in columns:
        if column in request_args and request_args[column]:
            value = request_args[column]
            if table_name == 'items' and column == "Assigned To":
                where_clauses.append("e.name LIKE %s")
            elif table_name == 'items':
                where_clauses.append(f"i.`{column}` LIKE %s")
            else:
                where_clauses.append(f"`{column}` LIKE %s")
            filter_values.append(f"%{value}%")
    
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # --- Handle Sorting ---
    sort_column = request_args.get('sort_column') or request_args.get('column')
    sort_direction = request_args.get('sort_direction', 'asc')
    
    order_sql = ""
    if sort_column and sort_column in columns and sort_direction.lower() in ['asc', 'desc']:
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

    html = render_template(
        'pdf_template.html',  # Create a new template specifically for PDF
        items=items,
        columns=columns,
        table_name=table_name,
        current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        column_widths=calculate_column_widths(items, columns),
        zip = zip
    )

    # Generate PDF with proper CSS
    pdf = HTML(
        string=html,
        base_url=request.base_url  # Important for static files
    ).write_pdf(stylesheets=[
        CSS(string='''
            @page { 
            size: A4 landscape;  /* Landscape often works better for wide tables */
            margin: 1cm; 
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 8pt;
            }
            }
            body { 
                font-family: Arial; 
                font-size: 9pt;  /* Slightly smaller font */
                line-height: 1.3;
            }
            h1 { 
                color: #333; 
                text-align: center;
                margin-bottom: 0.5cm;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;  /* Essential for column control */
                display: flex
                flex-direction: row
            }
            th {
                background-color: #f2f2f2;
                text-align: left;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            td {
                padding: 4px;
                border: 1px solid #ddd;
                vertical-align: top;  /* Align content to top */
            }
            .timestamp {
                font-size: 8pt;       /* Smaller font for timestamps */
            }
            ''')
    ])

    # Output PDF as a downloadable file
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={table_name}_report.pdf'
    return response

@bp.route('/items/convert_pdf_qr')
@admin_required
def convert_pdf_qr():
    c = get_cursor()
    request_args = request.args.to_dict()

    # Columns and base query (same as your convert_pdf)
    columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
               'comment', 'Assigned To', 'department', 'last_updated']
    base_query = """
        SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
        i.comment, e.name AS 'Assigned To', i.department, i.last_updated
        FROM items i
        LEFT JOIN employees e ON i.employee = e.employee_id
    """

    # --- Handle Filters ---
    where_clauses = []
    filter_values = []
    for column in columns:
        if column in request_args and request_args[column]:
            value = request_args[column]
            if column == "Assigned To":
                where_clauses.append("e.name LIKE %s")
            else:
                where_clauses.append(f"i.`{column}` LIKE %s")
            filter_values.append(f"%{value}%")
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # --- Handle Sorting ---
    sort_column = request_args.get('sort_column') or request_args.get('column')
    sort_direction = request_args.get('sort_direction', 'asc')
    order_sql = ""
    if sort_column and sort_column in columns and sort_direction.lower() in ['asc', 'desc']:
        if sort_column == "Assigned To":
            order_sql = f" ORDER BY e.name {sort_direction}"
        else:
            order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"

    sql_query = base_query + where_sql + order_sql

    c.execute(sql_query, tuple(filter_values))
    items = c.fetchall()
    c.close()

    # --- Only include these columns in the QR code ---
    qr_columns = ['item_id', 'item_name', 'serial_number']  # Change as needed

    # Map column names to their index in the row
    col_indices = {col: idx for idx, col in enumerate(columns)}

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    page_width = 190
    qr_width = 25
    qr_height = 25
    spacing = 10
    max_per_row = page_width // (qr_width + spacing)
    x_start = 10
    y_start = 20
    x = x_start
    y = y_start

    for idx, row in enumerate(items):
        # Build QR data string with only the selected columns
        qr_data = "\n".join(f"{col}: {row[col_indices[col]]}" for col in qr_columns)
        qr_img = qrcode.make(qr_data)
        img_io = io.BytesIO()
        qr_img.save(img_io, format='PNG')
        img_io.seek(0)
        pdf.image(img_io, x=x, y=y, w=qr_width, h=qr_height, type='PNG')
        pdf.set_xy(x, y + qr_height)
        pdf.cell(qr_width, 5, f"{row[col_indices['item_id']]}", 0, 0, "C")

        x += qr_width + spacing
        if (idx + 1) % max_per_row == 0:
            x = x_start
            y += qr_height + 15
        if y + qr_height + 15 > 277:
            pdf.add_page()
            x = x_start
            y = y_start

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=items_qr_codes.pdf'
    return response