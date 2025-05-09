from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import datetime

from invemp.auth import admin_required
from invemp.dashboard_helpers import (
    is_valid_table, get_filters, get_dropdown_options, 
    get_entry, get_items_columns, get_items_query, get_preserved_args
)
from invemp.db import get_cursor

bp = Blueprint('dashboard_admin', __name__)

@bp.route('/<table_name>/create', methods=('GET', 'POST'))
@admin_required
def create(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    preserved_args = get_preserved_args()

    c.execute(f"DESCRIBE `{table_name}`")
    if table_name == 'items':
        columns = get_items_columns()
    else:
        columns = [row[0] for row in c.fetchall()]
    c.close()


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
            if table_name == 'items':
                if max_id is None:
                    next_id = "MLQU-0000001"
                elif isinstance(max_id, str) and max_id.startswith('MLQU-'):
                    num_part = max_id.split('-')[-1]
                    next_num = int(num_part) + 1 if num_part.isdigit() else 1
                    next_id = f"MLQU-{next_num:07d}"
                else:
                    # fallback if max_id is not in expected format
                    next_id = "MLQU-0000001"
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
            elif column == 'status':
                continue
            elif column == 'Assigned To':
                # Convert employee name to employee_id before inserting
                assigned_to_name = request.form.get('Assigned To')
                # Convert name to employee_id
                if assigned_to_name:
                    c_lookup = get_cursor()
                    c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
                    emp_row = c_lookup.fetchone()
                    c_lookup.close()
                    assigned_to_value = emp_row[0] if emp_row else None
                else:
                    assigned_to_value = None
                values.append(assigned_to_value)
                insert_columns.append('employee')
            else:
                if request.form.get(column) != '':
                    values.append(request.form.get(column))
                else:
                    values.append(None)
                insert_columns.append(column)

        status_from_form = request.form.get('status', '').strip().lower()

        # Handle status logic
        if status_from_form in ['for disposal', 'for repair']:
            values.append(status_from_form)
        elif assigned_to_value:  # Not empty/None/Null
            values.append('assigned')
        else:
            values.append('active')
        insert_columns.append('status')

        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO `{table_name}` ({', '.join(insert_columns)}) VALUES ({placeholders})"

        try:
            c = get_cursor()
            c.execute(query, values)
            c.connection.commit()
            c.close()
            preserved_args = get_preserved_args()
            flash(f"Successfully created new {table_name[:-1]}")
            return redirect(url_for('dashboard_user.index', table_name=table_name,
                                    **preserved_args))
        except Exception as e:
            # Import pymysql.err if not already imported
            import pymysql
            if isinstance(e, pymysql.err.IntegrityError):
                flash(f"Integrity Error: {e}", "error")
            else:
                flash(f"Database Error: {e}", "error")
            if c:
                c.close()
            
            # Prepare entry from form data to keep user input
            entry = []
            for column in columns:
                if column == 'id' or column.endswith('_id') or column == 'ID':
                    entry.append(id)
                elif column == 'Assigned To':
                    entry.append(request.form.get('Assigned To'))
                elif column == 'last_updated':
                    entry.append(current_datetime)
                else:
                    entry.append(request.form.get(column))
            return render_template('dashboard/create.html', table_name=table_name, entry=entry,
                           columns=columns, dropdown_options=dropdown_options, preserved_args=preserved_args)
        
    return render_template('dashboard/create.html', table_name=table_name, 
                           columns=columns, dropdown_options=dropdown_options,
                           preserved_args=preserved_args)

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

    preserved_args = get_preserved_args()

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
                assigned_to_name = request.form.get('Assigned To')
                # Convert name to employee_id
                if assigned_to_name:
                    c_lookup = get_cursor()
                    c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
                    emp_row = c_lookup.fetchone()
                    c_lookup.close()
                    assigned_to_value = emp_row[0] if emp_row else None
                else:
                    assigned_to_value = None
                column = 'employee'
                values.append(assigned_to_value)
                update_columns.append(column)
            elif column == 'status':
                continue
            elif column == 'last_updated':
                values.append(current_datetime)
                update_columns.append(column)
            else:
                if request.form.get(column) != '':
                    values.append(request.form.get(column))
                else:
                    values.append(None)
                update_columns.append(column)

        status_from_form = request.form.get('status', '').strip().lower()

        # Handle status logic
        if status_from_form in ['for disposal', 'for repair']:
            values.append(status_from_form)
        elif assigned_to_value:  # Not empty/None/Null
            values.append('assigned')
        else:
            values.append('active')
        update_columns.append('status')

        placeholders = ', '.join([f"`{col}` = %s" for col in update_columns])
        query = f"UPDATE `{table_name}` SET {placeholders} WHERE `{id_column}` = %s"
        values.append(id)

        try:
            c = get_cursor()
            c.execute(query, values)
            c.connection.commit()
            c.close()
            flash(f"Successfully updated {table_name} id: {entry[0]}")
            return redirect(url_for('dashboard_user.index', table_name=table_name,
                                    **preserved_args))
        except Exception as e:
            # Import pymysql.err if not already imported
            import pymysql
            if isinstance(e, pymysql.err.IntegrityError):
                flash(f"Integrity Error: {e}", "error")
            else:
                flash(f"Database Error: {e}", "error")
            if c:
                c.close()
            
            # Prepare entry from form data to keep user input
            entry = []
            for column in columns:
                if column == 'id' or column.endswith('_id') or column == 'ID':
                    entry.append(id)
                elif column == 'Assigned To':
                    entry.append(request.form.get('Assigned To'))
                elif column == 'last_updated':
                    entry.append(current_datetime)
                else:
                    entry.append(request.form.get(column))
            # Stay on the update page with the user's input preserved
            return render_template(
                'dashboard/update.html',
                entry=entry,
                table_name=table_name,
                columns=columns,
                dropdown_options=dropdown_options,
                preserved_args=preserved_args
            )

    return render_template('dashboard/update.html', entry=entry, table_name=table_name, columns=columns, 
                           dropdown_options=dropdown_options, preserved_args=preserved_args)

@bp.route('/<table_name>/<id>/archive_scrap', methods=('GET', 'POST'))
@admin_required
def archive_scrap(id, table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    preserved_args = get_preserved_args()

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
    preserved_args = get_preserved_args()

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
    
    return redirect(url_for('dashboard_user.index', table_name = table_name, **preserved_args))