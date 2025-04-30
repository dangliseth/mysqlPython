from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import datetime

from invemp.auth import admin_required
from invemp.dashboard_helpers import (
    is_valid_table, get_filters, get_dropdown_options, 
    get_entry, get_items_columns, get_items_query
)
from invemp.db import get_cursor

bp = Blueprint('dashboard_admin', __name__)

@bp.route('/<table_name>/create', methods=('GET', 'POST'))
@admin_required
def create(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    if table_name == 'items':
        columns = get_items_columns()
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
    if request.method == 'POST':
        if id_column:
            c = get_cursor()
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
        return redirect(url_for('dashboard_user.index', table_name=table_name, filters = filters))
    return render_template('dashboard/create.html', table_name=table_name, 
                           columns=columns, dropdown_options=dropdown_options, filters = filters)

@bp.route('/<table_name>/<id>/update', methods=('GET', 'POST'))
@admin_required
def update(id, table_name):
    if not is_valid_table(table_name):
        abort(400)
    entry = get_entry(id, table_name)
    entry = list(entry)
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    if table_name == 'items':
        columns = get_items_columns()
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
            if column == 'password':
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


        flash(f"Successfully updated {table_name} id: {entry[0]}")
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    return render_template('dashboard/update.html', entry=entry, table_name=table_name, columns=columns, 
                           dropdown_options=dropdown_options, filters = filters)

@bp.route('/<table_name>/<id>/archive_scrap', methods=('GET', 'POST'))
@admin_required
def archive_scrap(id, table_name):
    if not is_valid_table(table_name):
        abort(400)
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
    return redirect(url_for('dashboard_user.index', table_name = table_name))

@bp.route('/<table_name>/<id>/delete', methods=('GET', 'POST'))
def delete(id, table_name):
    if not is_valid_table(table_name):
        abort(400)
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
    
    return redirect(url_for('dashboard_user.index', table_name = table_name, filters = filters))