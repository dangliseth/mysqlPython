from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, send_file, jsonify
)
from werkzeug.exceptions import abort

import datetime
import os
import tempfile
import pandas as pd
import re

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
        describe_rows = [row for row in c.fetchall()]
    else:
        describe_rows = c.fetchall()
        columns = [row[0] for row in describe_rows]
    # Build not_null_columns dict
    not_null_columns = {row[0]: (row[2] == 'NO') for row in describe_rows}
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

        # Only handle 'employee', 'department', and 'status' columns for items table
        if table_name == 'items':
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

            if status_from_form == 'active':
                values.append('MIS')
                insert_columns.append('department')
                values.append(status_from_form)
            elif status_from_form == 'assigned' and assigned_to_value is None:
                flash("'Assigned To' column cannot be empty when status is 'assigned'.", "error")
                entries = preserve_current_entries(columns)
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
        else:
            # For non-items tables, only add department/status if they exist in columns
            if 'department' in columns:
                values.append(department_value)
                insert_columns.append('department')
            if 'status' in columns:
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
                           columns=columns, dropdown_options=dropdown_options, preserved_args=preserved_args, not_null_columns=not_null_columns)
    
    return render_template('dashboard/create.html', table_name=table_name, 
                           columns=columns, dropdown_options=dropdown_options,
                           preserved_args=preserved_args, not_null_columns=not_null_columns)

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
        describe_rows = [row for row in c.fetchall()]
    else:
        describe_rows = c.fetchall()
        columns = [row[0] for row in describe_rows]
    # Build not_null_columns dict
    not_null_columns = {row[0]: (row[2] == 'NO') for row in describe_rows}
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
                    # Close previous assignment (set removed_date)
                    if prev_assigned_to_value:
                        c.execute(
                            """
                            UPDATE item_assignment_history
                            SET removed_date = %s
                            WHERE item_id = %s AND employee_id = %s AND removed_date IS NULL
                            """,
                            (current_datetime, id, prev_assigned_to_value)
                        )
                    # Add new assignment if new_assigned_to_value is not None
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
                preserved_args=preserved_args,
                not_null_columns=not_null_columns
            )
    return render_template('dashboard/update.html', entry=entry, table_name=table_name, columns=columns, 
                           dropdown_options=dropdown_options, preserved_args=preserved_args, not_null_columns=not_null_columns)

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

@bp.route('/import_data', methods=['POST'])
@admin_required
def import_data():
    file = request.files.get('file')
    if not file:
        flash('No file uploaded.', 'error')
        return redirect(url_for('dashboard_user.index', table_name='items'))
    try:
        c = get_cursor()
        table_name = 'items'
        c.execute(f"DESCRIBE `{table_name}`")
        describe_rows = c.fetchall()
        db_columns = [row[0] for row in describe_rows]
        not_null_columns = {row[0]: (row[2] == 'NO') for row in describe_rows}
        c.close()
        def normalize(col):
            return re.sub(r'[^a-z0-9]', '', str(col).lower())
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            file.save(tmp.name)
            xl = pd.ExcelFile(tmp.name)
            if len(xl.sheet_names) > 1:
                # Store the temp file path and sheet names in session for next request
                import flask
                flask.session['import_tempfile'] = tmp.name
                flask.session['import_sheets'] = xl.sheet_names
                # Do NOT delete here; file needed for next request
                return render_template('dashboard/select_sheet.html', sheets=xl.sheet_names, table_name=table_name)
            df = xl.parse(xl.sheet_names[0])
        # Now safe to delete temp file
        os.unlink(tmp.name)
        if df.empty:
            flash('Excel file is empty.', 'error')
            return redirect(url_for('dashboard_user.index', table_name=table_name))
        headers = list(df.columns)
        normalized_headers = [normalize(h) for h in headers]
        db_norm_map = {normalize(col): col for col in db_columns}
        excel_to_db = {}
        for idx, norm in enumerate(normalized_headers):
            if norm in db_norm_map and db_norm_map[norm] not in ['id', 'item_id', 'employee_id']:
                excel_to_db[idx] = db_norm_map[norm]
        # Check for required columns (except id types)
        id_types = ['id', 'item_id', 'employee_id']
        missing_required = [col for col, required in not_null_columns.items() if required and col not in excel_to_db.values() and col not in id_types]
        if missing_required:
            flash(f"Missing required columns: {', '.join(missing_required)}", 'error')
            return redirect(url_for('dashboard_user.index', table_name=table_name))
        # Insert each row
        c = get_cursor()
        inserted = 0
        # --- ID generation logic (supporting id, item_id, employee_id) ---
        # Find which id column exists in db_columns
        id_column = None
        for possible_id in ['item_id', 'employee_id', 'id']:
            if possible_id in db_columns:
                id_column = possible_id
                break
        # Generate next_id based on id_column type
        if id_column == 'item_id':
            c.execute(f"SELECT MAX(item_id) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            if max_id is None:
                next_id = "MLQU-0000001"
            elif isinstance(max_id, str) and max_id.startswith('MLQU-'):
                num_part = max_id.split('-')[-1]
                next_num = int(num_part) + 1 if num_part.isdigit() else 1
                next_id = f"MLQU-{next_num:07d}"
            else:
                next_id = "MLQU-0000001"
        elif id_column == 'employee_id':
            c.execute(f"SELECT MAX(CAST(employee_id AS UNSIGNED)) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            next_id = (int(max_id) if max_id is not None else 0) + 1
        elif id_column == 'id':
            c.execute(f"SELECT MAX(CAST(id AS UNSIGNED)) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            next_id = (int(max_id) if max_id is not None else 0) + 1
        else:
            next_id = None
        # Track unrecognized headers for each row
        recognized_norms = set([normalize(v) for v in excel_to_db.values()])
        # Find the actual column name for 'description' if present
        description_col = None
        for col in db_columns:
            if normalize(col) == 'description':
                description_col = col
                break
        for _, row in df.iterrows():
            values = []
            insert_columns = []
            # Always generate new ID
            row_id = next_id
            # Prepare for next id
            if id_column == 'item_id':
                num_part = int(str(row_id).split('-')[-1])
                next_id = f"MLQU-{num_part+1:07d}"
            elif id_column in ['employee_id', 'id']:
                next_id += 1
            assigned_to_value = None
            status_value = None
            department_value = None
            # Collect unrecognized header data for this row
            unrec_data = []
            # --- Collect duplicate header values ---
            # Build a map: normalized header -> list of (original header, index)
            header_map = {}
            for idx, header in enumerate(headers):
                norm = normalize(header)
                header_map.setdefault(norm, []).append((header, idx))
            # For each normalized header with multiple columns, join their values
            duplicate_values = {}
            for norm, header_list in header_map.items():
                if len(header_list) > 1:
                    vals = []
                    for header, idx in header_list:
                        val = row[header]
                        if not pd.isna(val) and str(val).strip() != '':
                            vals.append(str(val).strip())
                    if vals:
                        duplicate_values[norm] = ' | '.join(vals)
            # Unrecognized headers (not mapped to DB columns)
            for norm, header_list in header_map.items():
                if norm not in recognized_norms and norm not in ['id','itemid','employeeid']:
                    for header, idx in header_list:
                        val = row[header]
                        if not pd.isna(val) and str(val).strip() != '':
                            unrec_data.append(f"{header}: {val}")
            for db_col in db_columns:
                if db_col == id_column:
                    values.append(row_id)
                    insert_columns.append(db_col)
                    continue
                # Handle 'employee' (from 'Assigned To')
                if db_col == 'employee':
                    assigned_to_idx = None
                    for idx, v in excel_to_db.items():
                        if v.lower() == 'assigned to':
                            assigned_to_idx = idx
                            break
                    assigned_to_name = row[headers[assigned_to_idx]] if assigned_to_idx is not None else None
                    if pd.isna(assigned_to_name) or not assigned_to_name:
                        assigned_to_value = None
                    else:
                        c_lookup = get_cursor()
                        c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
                        emp_row = c_lookup.fetchone()
                        c_lookup.close()
                        assigned_to_value = emp_row[0] if emp_row else None
                    values.append(assigned_to_value)
                    insert_columns.append(db_col)
                    continue
                if db_col == 'status':
                    status_idx = None
                    for idx, v in excel_to_db.items():
                        if v.lower() == 'status':
                            status_idx = idx
                            break
                    status_value = row[headers[status_idx]].strip().lower() if status_idx is not None and not pd.isna(row[headers[status_idx]]) else None
                    values.append(status_value)
                    insert_columns.append(db_col)
                    continue
                if db_col == 'department':
                    department_idx = None
                    for idx, v in excel_to_db.items():
                        if v.lower() == 'department':
                            department_idx = idx
                            break
                    department_value = row[headers[department_idx]] if department_idx is not None and not pd.isna(row[headers[department_idx]]) else None
                    values.append(department_value)
                    insert_columns.append(db_col)
                    continue
                # If this is the description column, append unrecognized data
                if description_col and db_col == description_col:
                    # Get value from Excel if present (including duplicates)
                    desc_val = ''
                    desc_norm = normalize('description')
                    if desc_norm in duplicate_values:
                        desc_val = duplicate_values[desc_norm]
                    else:
                        # If only one, get it from excel_to_db
                        desc_idx = None
                        for idx, v in excel_to_db.items():
                            if v.lower() == 'description':
                                desc_idx = idx
                                break
                        if desc_idx is not None:
                            val = row[headers[desc_idx]]
                            if not pd.isna(val):
                                desc_val = str(val).strip()
                    # Append unrecognized data
                    if unrec_data:
                        if desc_val:
                            desc_val = desc_val + ' | ' + ' | '.join(unrec_data)
                        else:
                            desc_val = ' | '.join(unrec_data)
                    values.append(desc_val)
                    insert_columns.append(db_col)
                    continue
                # Default: normal mapping, but join duplicate header values if present
                norm_db_col = normalize(db_col)
                if norm_db_col in duplicate_values:
                    val = duplicate_values[norm_db_col]
                elif db_col in excel_to_db.values():
                    idx = [k for k, v in excel_to_db.items() if v == db_col][0]
                    val = row[headers[idx]]
                    if pd.isna(val):
                        val = None
                else:
                    val = None
                if not_null_columns[db_col] and (val is None or str(val).strip() == ''):
                    break
                values.append(val)
                insert_columns.append(db_col)
            else:
                placeholders = ', '.join(['%s'] * len(values))
                query = f"INSERT INTO `{table_name}` ({', '.join(insert_columns)}) VALUES ({placeholders})"
                try:
                    c.execute(query, values)
                    inserted += 1
                except Exception as e:
                    continue
        c.connection.commit()
        c.close()
        flash(f"Imported {inserted} rows from Excel.", 'success')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    except Exception as e:
        flash(f'Error importing Excel file: {e}', 'error')
        return redirect(url_for('dashboard_user.index', table_name='items'))

@bp.route('/import_data_select_sheet', methods=['POST'])
@admin_required
def import_data_select_sheet():
    import flask
    table_name = request.args.get('table_name', 'items')
    sheet = request.form.get('sheet')
    temp_path = flask.session.get('import_tempfile')
    sheets = flask.session.get('import_sheets')
    if not temp_path or not sheet or not sheets or sheet not in sheets:
        flash('Invalid sheet selection or session expired.', 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    try:
        c = get_cursor()
        c.execute(f"DESCRIBE `{table_name}`")
        describe_rows = c.fetchall()
        db_columns = [row[0] for row in describe_rows]
        not_null_columns = {row[0]: (row[2] == 'NO') for row in describe_rows}
        c.close()
        def normalize(col):
            return re.sub(r'[^a-z0-9]', '', str(col).lower())
        xl = pd.ExcelFile(temp_path)
        df = xl.parse(sheet)
        # Now safe to delete temp file
        os.unlink(temp_path)
        flask.session.pop('import_tempfile', None)
        flask.session.pop('import_sheets', None)
        if df.empty:
            flash('Excel sheet is empty.', 'error')
            return redirect(url_for('dashboard_user.index', table_name=table_name))
        headers = list(df.columns)
        normalized_headers = [normalize(h) for h in headers]
        db_norm_map = {normalize(col): col for col in db_columns}
        excel_to_db = {}
        for idx, norm in enumerate(normalized_headers):
            if norm in db_norm_map and db_norm_map[norm] not in ['id', 'item_id', 'employee_id']:
                excel_to_db[idx] = db_norm_map[norm]
        id_types = ['id', 'item_id', 'employee_id']
        missing_required = [col for col, required in not_null_columns.items() if required and col not in excel_to_db.values() and col not in id_types]
        if missing_required:
            flash(f"Missing required columns: {', '.join(missing_required)}", 'error')
            return redirect(url_for('dashboard_user.index', table_name=table_name))
        c = get_cursor()
        inserted = 0
        id_column = None
        for possible_id in ['item_id', 'employee_id', 'id']:
            if possible_id in db_columns:
                id_column = possible_id
                break
        if id_column == 'item_id':
            c.execute(f"SELECT MAX(item_id) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            if max_id is None:
                next_id = "MLQU-0000001"
            elif isinstance(max_id, str) and max_id.startswith('MLQU-'):
                num_part = max_id.split('-')[-1]
                next_num = int(num_part) + 1 if num_part.isdigit() else 1
                next_id = f"MLQU-{next_num:07d}"
            else:
                next_id = "MLQU-0000001"
        elif id_column == 'employee_id':
            c.execute(f"SELECT MAX(CAST(employee_id AS UNSIGNED)) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            next_id = (int(max_id) if max_id is not None else 0) + 1
        elif id_column == 'id':
            c.execute(f"SELECT MAX(CAST(id AS UNSIGNED)) AS max_id FROM `{table_name}`")
            max_id = c.fetchone()[0]
            next_id = (int(max_id) if max_id is not None else 0) + 1
        else:
            next_id = None
        recognized_norms = set([normalize(v) for v in excel_to_db.values()])
        description_col = None
        for col in db_columns:
            if normalize(col) == 'description':
                description_col = col
                break
        for _, row in df.iterrows():
            values = []
            insert_columns = []
            row_id = next_id
            if id_column == 'item_id':
                num_part = int(str(row_id).split('-')[-1])
                next_id = f"MLQU-{num_part+1:07d}"
            elif id_column in ['employee_id', 'id']:
                next_id += 1
            assigned_to_value = None
            status_value = None
            department_value = None
            unrec_data = []
            header_map = {}
            for idx, header in enumerate(headers):
                norm = normalize(header)
                header_map.setdefault(norm, []).append((header, idx))
            duplicate_values = {}
            for norm, header_list in header_map.items():
                if len(header_list) > 1:
                    vals = []
                    for header, idx in header_list:
                        val = row[header]
                        if not pd.isna(val) and str(val).strip() != '':
                            vals.append(str(val).strip())
                    if vals:
                        duplicate_values[norm] = ' | '.join(vals)
            for norm, header_list in header_map.items():
                if norm not in recognized_norms and norm not in ['id','itemid','employeeid']:
                    for header, idx in header_list:
                        val = row[header]
                        if not pd.isna(val) and str(val).strip() != '':
                            unrec_data.append(f"{header}: {val}")
            for db_col in db_columns:
                if db_col == id_column:
                    values.append(row_id)
                    insert_columns.append(db_col)
                    continue
                # Handle 'employee' (from 'Assigned To')
                if db_col == 'employee':
                    assigned_to_idx = None
                    for idx, v in excel_to_db.items():
                        if v.lower() == 'assigned to':
                            assigned_to_idx = idx
                            break
                    assigned_to_name = row[headers[assigned_to_idx]] if assigned_to_idx is not None else None
                    if pd.isna(assigned_to_name) or not assigned_to_name:
                        assigned_to_value = None
                    else:
                        c_lookup = get_cursor()
                        c_lookup.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
                        emp_row = c_lookup.fetchone()
                        c_lookup.close()
                        assigned_to_value = emp_row[0] if emp_row else None
                    values.append(assigned_to_value)
                    insert_columns.append(db_col)
                    continue
                if db_col == 'status':
                    status_idx = None
                    for idx, v in excel_to_db.items():
                        if v.lower() == 'status':
                            status_idx = idx
                            break
                    status_value = row[headers[status_idx]].strip().lower() if status_idx is not None and not pd.isna(row[headers[status_idx]]) else None
                    values.append(status_value)
                    insert_columns.append(db_col)
                    continue
                if db_col == 'department':
                    department_idx = None
                    for idx, v in excel_to_db.items():
                        if v.lower() == 'department':
                            department_idx = idx
                            break
                    department_value = row[headers[department_idx]] if department_idx is not None and not pd.isna(row[headers[department_idx]]) else None
                    values.append(department_value)
                    insert_columns.append(db_col)
                    continue
                # If this is the description column, append unrecognized data
                if description_col and db_col == description_col:
                    desc_val = ''
                    desc_norm = normalize('description')
                    if desc_norm in duplicate_values:
                        desc_val = duplicate_values[desc_norm]
                    else:
                        desc_idx = None
                        for idx, v in excel_to_db.items():
                            if v.lower() == 'description':
                                desc_idx = idx
                                break
                        if desc_idx is not None:
                            val = row[headers[desc_idx]]
                            if not pd.isna(val):
                                desc_val = str(val).strip()
                    if unrec_data:
                        if desc_val:
                            desc_val = desc_val + ' | ' + ' | '.join(unrec_data)
                        else:
                            desc_val = ' | '.join(unrec_data)
                    values.append(desc_val)
                    insert_columns.append(db_col)
                    continue
                norm_db_col = normalize(db_col)
                if norm_db_col in duplicate_values:
                    val = duplicate_values[norm_db_col]
                elif db_col in excel_to_db.values():
                    idx = [k for k, v in excel_to_db.items() if v == db_col][0]
                    val = row[headers[idx]]
                    if pd.isna(val):
                        val = None
                else:
                    val = None
                if not_null_columns[db_col] and (val is None or str(val).strip() == ''):
                    break
                values.append(val)
                insert_columns.append(db_col)
            else:
                placeholders = ', '.join(['%s'] * len(values))
                query = f"INSERT INTO `{table_name}` ({', '.join(insert_columns)}) VALUES ({placeholders})"
                try:
                    c.execute(query, values)
                    inserted += 1
                except Exception as e:
                    continue
        c.connection.commit()
        c.close()
        flash(f"Imported {inserted} rows from Excel.", 'success')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    except Exception as e:
        flash(f'Error importing Excel file: {e}', 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))