from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import datetime

from invemp.auth import login_required, admin_required
from invemp.db import get_cursor

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@admin_required
def index():
    c = get_cursor()
    c.execute('SHOW TABLES')
    tables = [table[0] for table in c.fetchall()]
    c.close()

    return render_template('dashboard/index.html', tables=tables)

@bp.route('/view_table/<table_name>')
@login_required
def view_table(table_name):
    # check for admin access
    if g.user[3] != 'admin' and table_name != 'items':
        flash("You do not have permission to access this table.")
        return redirect(url_for('dashboard.index'))
    

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
    else:
        # Generic query for other tables
        c.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        items = c.fetchall()
        columns = [column[0] for column in c.description]
    c.close()
    return render_template('dashboard/view_table.html', items=items, columns=columns, table_name=table_name)

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

@bp.route('/view_table/<table_name>/create', methods=('GET', 'POST'))
@admin_required
def create(table_name):
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()

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
    return render_template('dashboard/create.html', table_name=table_name, columns=columns)

@bp.route('/view_table/<table_name>/<int:id>/update', methods=('GET', 'POST'))
@admin_required
def update(id, table_name):
    entry = get_entry(id, table_name)
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()
    current_datetime = datetime.datetime.now()

    if request.method == 'POST':
        values = []
        for column in columns:
            if column == 'id' or column.endswith('_id') or column == 'ID':  # Skip ID columns
                continue
            if column == 'last_updated':
                values.append(current_datetime)
            else:
                values.append(request.form.get(column))

        placeholders = ', '.join([f"`{col}` = %s" for col in columns])
        query = f"UPDATE `{table_name}` SET {placeholders} WHERE `{columns[0]}` = %s"
        values.append(id)

        c = get_cursor()
        c.execute(query, values)
        c.connection.commit()
        c.close()

        flash(f"Successfully updated {table_name[:-1]}")
        return redirect(url_for('dashboard.view_table', table_name=table_name))
    return render_template('dashboard/update.html', entry=entry, table_name=table_name, columns=columns)