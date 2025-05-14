from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import datetime

from invemp.auth import admin_required
from invemp.dashboard_helpers import (
    is_valid_table, get_dropdown_options, 
    get_entry, get_items_columns, get_preserved_args,
    get_item_assignment_history, preserve_current_entries
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
                continue
            elif column == 'department':
                continue
            else:
                if request.form.get(column) != '':
                    values.append(request.form.get(column))
                else:
                    values.append(None)
                insert_columns.append(column)


        status_from_form = request.form.get('status', '').strip().lower()
        department_value = request.form.get('department')
        # Convert employee name to employee_id before inserting
        assigned_to_name = request.form.get('Assigned To')

        # Convert name to employee_id
        if assigned_to_name and status_from_form != 'active':
            c_lookup = get_cursor()
            c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
            emp_row = c_lookup.fetchone()
            c_lookup.close()
            assigned_to_value = emp_row[0] if emp_row else None
        else:
            assigned_to_value = None
        values.append(assigned_to_value)
        insert_columns.append('employee')

        # Handle status logic
        if status_from_form == 'active':
            values.append('MIS')
            insert_columns.append('department')
            values.append(status_from_form)
        elif status_from_form == 'assigned' and assigned_to_value is None:
            flash("'Assigned To' column cannot be empty when status is 'assigned'.", "error")
            entries = preserve_current_entries(columns)
            # Stay on the update page with the user's input preserved
            return render_template(
                'dashboard/create.html',
                entries=entries,
                table_name=table_name,
                columns=columns,
                dropdown_options=dropdown_options,
                preserved_args=preserved_args
            )
        else:
            values.append(department_value)
            insert_columns.append('department')
            values.append(status_from_form)
        insert_columns.append('status')

        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO `{table_name}` ({', '.join(insert_columns)}) VALUES ({placeholders})"

        try:
            c = get_cursor()
            c.execute(query, values)
            c.connection.commit()
            # --- Item Assignment History Logic ---
            if table_name == 'items' and assigned_to_value:
                c.execute(
                    """
                    INSERT INTO item_assignment_history (item_id, employee_id, assigned_date)
                    VALUES (%s, %s, %s)
                    """,
                    (next_id, assigned_to_value, current_datetime)
                )
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
        prev_assigned_to_value = None
        new_assigned_to_value = None
        for column in columns:
            if column == 'id' or column.endswith('_id') or column == 'ID':  # Skip ID columns
                id_column = column
                continue
            if column == 'password':
                continue
            elif column == 'status':
                continue
            elif column == 'Assigned To':
                continue
            elif column == 'department':
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

        # Get previous assigned_to_value (employee_id) from DB
        if table_name == 'items':
            c_prev = get_cursor()
            c_prev.execute("SELECT employee FROM items WHERE item_id = %s", (id,))
            prev_row = c_prev.fetchone()
            if prev_row:
                prev_assigned_to_value = prev_row[0]
            c_prev.close()

        # Handle status, 'Assigned To', and department logic
        assigned_to_name = request.form.get('Assigned To')
        department_value = request.form.get('department')
        status_from_form = request.form.get('status', '').strip().lower()
        # Convert name to employee_id
        if assigned_to_name and status_from_form != 'active':
            c_lookup = get_cursor()
            c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
            emp_row = c_lookup.fetchone()
            c_lookup.close()
            assigned_to_value = emp_row[0] if emp_row else None
        else:
            assigned_to_value = None
        employee_column = 'employee'
        values.append(assigned_to_value)
        update_columns.append(employee_column)
        new_assigned_to_value = assigned_to_value

        if status_from_form == 'active':
            values.append('MIS')
            update_columns.append('department')
            values.append(status_from_form)
        elif status_from_form == 'assigned' and assigned_to_value is None:
            flash("'Assigned To' column cannot be empty when status is 'assigned'.", "error")
            entries = preserve_current_entries(columns)
            # Stay on the update page with the user's input preserved
            return render_template(
                'dashboard/update.html',
                entry=entry,
                entries=entries,
                table_name=table_name,
                columns=columns,
                dropdown_options=dropdown_options,
                preserved_args=preserved_args
            )
        else:
            values.append(department_value)
            update_columns.append('department')
            values.append(status_from_form)
        update_columns.append('status')



        placeholders = ', '.join([f"`{col}` = %s" for col in update_columns])
        query = f"UPDATE `{table_name}` SET {placeholders} WHERE `{id_column}` = %s"
        values.append(id)

        try:
            c = get_cursor()
            c.execute(query, values)
            # --- Item Assignment History Logic ---
            if table_name == 'items':
                # If assignment changed, close previous and add new
                if prev_assigned_to_value != new_assigned_to_value:
                    # Set removed_date for previous assignment
                    if prev_assigned_to_value:
                        c.execute(
                            """
                            UPDATE item_assignment_history
                            SET removed_date = %s
                            WHERE item_id = %s AND employee_id = %s AND removed_date IS NULL
                            """,
                            (current_datetime, id, prev_assigned_to_value)
                        )
                    # Add new assignment if assigned
                    if new_assigned_to_value:
                        c.execute(
                            """
                            INSERT INTO item_assignment_history (item_id, employee_id, assigned_date)
                            VALUES (%s, %s, %s)
                            """,
                            (id, new_assigned_to_value, current_datetime)
                        )
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
            entries = preserve_current_entries(columns)
            # Stay on the update page with the user's input preserved
            return render_template(
                'dashboard/update.html',
                entry=entry,
                entries=entries,
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
    return redirect(url_for('dashboard_user.index', table_name = table_name, **preserved_args))

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
        if column == 'id' or column.endswith('_id') or column == 'ID':  # Determine id column
            id_column = column
            break

    if request.method == 'POST':
        c = get_cursor()
        if table_name == 'items':
            # Delete all assignment history for this item
            c.execute("DELETE FROM item_assignment_history WHERE item_id = %s", (id,))
        delete_query = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
        c.execute(delete_query, (id,)) 
        c.connection.commit()
        flash(f"{id_column}: {id} DELETED from {table_name}")
    return redirect(url_for('dashboard_user.index', table_name = table_name, **preserved_args))

@bp.route('/<table_name>/<id>/history', methods=('GET', 'POST'))
@admin_required
def history(id, table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    preserved_args = get_preserved_args()

    history_data = get_item_assignment_history(id)
    columns = ['item_id', 'employee_id', 'assigned_date', 'removed_date']
    
    c.close()
    
    return render_template('dashboard/history.html', table_name=table_name, 
                           history_data=history_data, columns=columns, zip=zip, 
                           preserved_args=preserved_args)