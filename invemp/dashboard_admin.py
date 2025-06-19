from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, send_file, jsonify, session
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

@bp.route('/<table_name>/create', methods=['GET', 'POST'])
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

@bp.route('/<table_name>/<id>/update', methods=['GET', 'POST'])
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


def normalize_column_name(column):
    """Normalize column name for comparison by removing special characters and converting to lowercase"""
    # Convert to lowercase and replace spaces/special chars with underscores
    normalized = str(column).lower().strip()
    normalized = re.sub(r'[\s\(\)\[\]\{\}]+', '_', normalized)  # Replace spaces and brackets with underscore
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)  # Remove any other special characters
    normalized = re.sub(r'_+', '_', normalized)  # Replace multiple underscores with single
    normalized = normalized.strip('_')  # Remove leading/trailing underscores
    return normalized

def load_options_from_file(filename):
    """Helper function to load allowed options from a text file"""
    file_path = os.path.join('invemp', 'static', 'options', filename)
    print(f"\nTrying to load options from: {file_path}")  # Debug print
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            options = set()
            for line in f:
                line = line.strip()
                if line and not line.startswith('//'):  # Skip empty lines and comments
                    print(f"Found option: {line}")  # Debug print
                    options.add(line)
            print(f"Loaded {len(options)} options from {filename}")  # Debug print
            return options
    except FileNotFoundError:
        print(f"Warning: Could not find file {file_path}")  # Debug print
        return set()
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")  # Debug print
        return set()

def bulk_insert_rows(c, table_name, valid_rows, current_datetime):
    """Helper function to handle bulk insertion with proper ID generation and relationships"""
    inserted = 0
    
    # Find ID column
    c.execute(f"DESCRIBE `{table_name}`")
    db_columns = [row[0] for row in c.fetchall()]
    id_column = next((col for col in db_columns if col == 'id' or col.endswith('_id')), None)

    if id_column:
        # Get current max ID
        c.execute(f"SELECT MAX({id_column}) AS max_id FROM `{table_name}`")
        max_id = c.fetchone()[0]

        if table_name == 'items':
            # Special format for items: MLQU-0000001
            if max_id is None:
                next_id = "MLQU-0000001"
                next_num = 1
            elif isinstance(max_id, str) and max_id.startswith('MLQU-'):
                num_part = max_id.split('-')[-1]
                next_num = int(num_part) + 1 if num_part.isdigit() else 1
            else:
                next_id = "MLQU-0000001"
                next_num = 1

            # Assign IDs to all valid rows
            for row_data in valid_rows:
                row_data[id_column] = f"MLQU-{next_num:07d}"
                next_num += 1
        else:
            # Simple incremental IDs for other tables
            next_id = (int(max_id) if max_id is not None else 0) + 1
            for row_data in valid_rows:
                row_data[id_column] = next_id
                next_id += 1

    # Process each row
    for row_data in valid_rows:
        try:
            # Add last_updated timestamp if it exists
            if 'last_updated' in db_columns:
                row_data['last_updated'] = current_datetime

            # Handle special case for items table: department = 'MIS' when status = 'active'
            if table_name == 'items' and row_data.get('status') == 'active':
                row_data['department'] = 'MIS'

            # Handle the case where status is 'assigned' but no valid employee
            if (table_name == 'items' and 
                row_data.get('status') == 'assigned' and 
                not row_data.get('employee')):
                continue  # Skip this row since it's invalid

            # Prepare and execute insert
            columns = list(row_data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"
            values = [row_data[col] for col in columns]

            c.execute(query, values)
            inserted += 1

            # Handle item assignment history if needed
            if (table_name == 'items' and 
                row_data.get('employee') and 
                row_data.get('status') != 'active'):
                c.execute(
                    """
                    INSERT INTO item_assignment_history (item_id, employee_id, assigned_date)
                    VALUES (%s, %s, %s)
                    """,
                    (row_data[id_column], row_data['employee'], current_datetime)
                )

        except Exception as e:
            flash(f"Error importing row with ID {row_data.get(id_column)}: {str(e)}", 'error')
            continue

    return inserted

@bp.route('/<table_name>/import', methods=['GET', 'POST'])
@admin_required
def import_data(table_name):
    if not is_valid_table(table_name):
        abort(400)

    # Load allowed options for dropdowns
    allowed_options = {
        'category': load_options_from_file('category.txt'),
        'department': load_options_from_file('department.txt'),
        'account_type': load_options_from_file('account_type.txt'),
        'status': load_options_from_file('status.txt')
    }
    
    print("\nDEBUG - Loaded department options:", sorted([opt for opt in allowed_options['department'] if not opt.startswith('//')]))
        
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
        
    # Check file extension
    if not file.filename.endswith('.xlsx'):
        flash('Please upload an Excel (.xlsx) file', 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
        
    temp_file = None
    xl = None
    try:
        # Create temporary file to store upload
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_file.name)
        temp_file.close()  # Close the file before pandas reads it
            
        # Read Excel file with pandas
        xl = pd.ExcelFile(temp_file.name)
            
        # If multiple sheets, store minimal info in session
        if len(xl.sheet_names) > 1:
            session['import_tempfile'] = temp_file.name
            session['import_sheets'] = xl.sheet_names
            xl.close()
            xl = None
            return render_template('dashboard/select_sheet.html', 
                               sheets=xl.sheet_names, 
                               table_name=table_name)
                                    
        # If single sheet, read it directly
        df = pd.read_excel(temp_file.name)
        xl.close()
        xl = None
            
        if df.empty:
            flash('Excel file is empty', 'error')
            return redirect(url_for('dashboard_user.index', table_name=table_name))

        # Get database columns and NOT NULL constraints
        c = get_cursor()
        try:
            c.execute(f"DESCRIBE `{table_name}`")
            describe_rows = c.fetchall()
            db_columns = [row[0] for row in describe_rows]
            not_null_columns = {row[0]: (row[2] == 'NO') for row in describe_rows}
            
            print("\nTable structure:")
            print("All columns:", db_columns)
            print("NOT NULL columns:", {col: req for col, req in not_null_columns.items() if req})
            
            # Process the data and insert immediately
            valid_rows = []
            total_rows = 0
            skipped_count = 0
            
            # Map Excel columns to database columns
            headers = list(df.columns)
            print("\nAllowed options:")  # Debug allowed options
            for opt_type, opt_values in allowed_options.items():
                print(f"{opt_type}: {sorted(opt_values)}")  # Show all values including case variations
            
            normalized_headers = [normalize_column_name(h) for h in headers]
            print("Normalized Headers:", normalized_headers)
            
            db_norm_map = {normalize_column_name(col): col for col in db_columns}
            print("DB Column Map:", db_norm_map)
            
            excel_to_db = {}
            
            # Map Excel columns to database columns with special cases
            for idx, norm_header in enumerate(normalized_headers):
                mapped = False
                # Handle special cases first
                if norm_header in ('assigned_to', 'assignedto') and 'employee' in db_columns:
                    excel_to_db[idx] = 'employee'
                    mapped = True
                elif norm_header in ('item_name', 'itemname') and 'name' in db_columns:
                    excel_to_db[idx] = 'name'
                    mapped = True
                elif norm_header in ('hard_drive', 'harddrive') and 'hard_drive' in db_columns:
                    excel_to_db[idx] = 'hard_drive'
                    mapped = True
                elif norm_header == 'avr' and 'avr' in db_columns:
                    excel_to_db[idx] = 'avr'
                    mapped = True
                
                # Try standard mapping if no special case matched
                if not mapped and norm_header in db_norm_map:
                    db_col = db_norm_map[norm_header]
                    if db_col not in ['id', 'item_id', 'employee_id']:
                        excel_to_db[idx] = db_col
                
                # Debug print for each mapping
                print(f"Header '{headers[idx]}' -> Normalized '{norm_header}' -> DB Column '{excel_to_db.get(idx, 'Not mapped')}'")

            # Show mapping in flash messages
            flash("Column mapping:", 'info')
            for idx, db_col in excel_to_db.items():
                flash(f"{headers[idx]} → {db_col}", 'info')

            # Check for missing required columns
            missing_required = []
            for col, required in not_null_columns.items():
                if required and col not in excel_to_db.values() and col not in ['id', 'item_id', 'employee_id', 'last_updated']:
                    missing_required.append(col)
            
            if missing_required:
                flash(f"Error: Missing required columns: {', '.join(missing_required)}", 'error')
                flash("Excel headers found: " + ", ".join(headers), 'info')
                return redirect(url_for('dashboard_user.index', table_name=table_name))

            # Process rows in batches to avoid memory issues
            batch_size = 100
            current_batch = []
            
            print("\nProcessing rows:")  # Debug header
            for idx, row in df.iterrows():
                total_rows += 1
                row_data = {}
                skip_row = False
                print(f"\nRow {idx}:")  # Debug for current row
                
                for excel_idx, db_col in excel_to_db.items():
                    value = row[headers[excel_idx]]
                    print(f"  Column '{db_col}': {value}")  # Debug column value
                    
                    # Handle employee lookup
                    if db_col == 'employee' and pd.notna(value):
                        assigned_to_name = str(value).strip()
                        status_value = None
                        
                        # Get status if it exists
                        for idx2, col in excel_to_db.items():
                            if col == 'status':
                                status_value = str(row[headers[idx2]]).strip().lower() if pd.notna(row[headers[idx2]]) else None
                                break
                        print(f"  Found status: {status_value}")  # Debug status
                        
                        # Only look up employee if status is not 'active'
                        if not status_value or status_value != 'active':
                            c.execute("SELECT employee_id FROM employees WHERE name = %s", (assigned_to_name,))
                            emp_row = c.fetchone()
                            value = emp_row[0] if emp_row else None
                            print(f"  Employee lookup for '{assigned_to_name}': {value}")  # Debug employee lookup
                        else:
                            value = None
                    
                    # Validate dropdown values
                    if db_col in allowed_options and pd.notna(value):
                        value_str = str(value).strip()
                        value_lower = value_str.lower()
                        
                        # Print debug info
                        print(f"  Validating {db_col}: '{value_str}'")
                        print(f"  Allowed values: {sorted(allowed_options[db_col])}")
                        
                        # Try exact match first
                        if value_str in allowed_options[db_col]:
                            value = value_str
                            print(f"  Exact match found")
                        else:
                            # Try case-insensitive match
                            matches = [opt for opt in allowed_options[db_col] 
                                     if opt.lower() == value_lower]
                            if matches:
                                value = matches[0]
                                print(f"  Case-insensitive match found: {value}")
                            else:
                                print(f"  No match found for {value_str} in {sorted(allowed_options[db_col])}")
                                skip_row = True
                                break
                    
                    # Check NOT NULL constraints
                    if not_null_columns.get(db_col, False):
                        if pd.isna(value) or str(value).strip() == '':
                            print(f"  Row {idx} skipped: Required column '{db_col}' is empty or NULL")  # Debug NULL constraint
                            skip_row = True
                            break
                    
                    row_data[db_col] = value
                
                if not skip_row:
                    print(f"  Row {idx} accepted with data: {row_data}")  # Debug accepted row
                    current_batch.append(row_data)
                    if len(current_batch) >= batch_size:
                        # Insert batch
                        inserted = bulk_insert_rows(c, table_name, current_batch, datetime.datetime.now())
                        valid_rows.extend(current_batch)
                        current_batch = []
                else:
                    print(f"  Row {idx} skipped!")  # Debug skipped row
                    skipped_count += 1
            
            # Insert any remaining rows
            if current_batch:
                inserted = bulk_insert_rows(c, table_name, current_batch, datetime.datetime.now())
                valid_rows.extend(current_batch)
            
            c.connection.commit()
            flash(f"Successfully imported {len(valid_rows)} out of {total_rows} rows. {skipped_count} rows were skipped.", 'success')
            
        except Exception as e:
            c.connection.rollback()
            flash(f"Error during import: {str(e)}", 'error')
        finally:
            c.close()
            
        return redirect(url_for('dashboard_user.index', table_name=table_name))
        
    except Exception as e:
        flash(f'Error processing Excel file: {str(e)}', 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    finally:
        # Clean up resources
        if xl is not None:
            xl.close()
        if temp_file is not None:
            try:
                os.unlink(temp_file.name)
            except (PermissionError, OSError):
                try:
                    import ctypes
                    MOVEFILE_DELAY_UNTIL_REBOOT = 4
                    ctypes.windll.kernel32.MoveFileExW(temp_file.name, None, MOVEFILE_DELAY_UNTIL_REBOOT)
                except:
                    pass
