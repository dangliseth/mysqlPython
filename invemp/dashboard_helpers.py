from flask import (
    request, flash
)

from invemp.db import get_cursor
from werkzeug.exceptions import abort

import datetime
import os

import re


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

def is_valid_table(table_name):
    allowed_tables = {'items', 'items_disposal', 'user_accounts', 'employees', 'employees_archive'}
    return table_name in allowed_tables

def get_dropdown_options():
    base_dir = os.path.join(os.path.dirname(__file__), 'static', 'options')
    def load_options(filename, fallback):
        path = os.path.join(base_dir, filename)
        try:
            with open(path, encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return fallback

    # Fallbacks in case files are missing
    fallback_category = ['Computer', 'Category 2', 'Category 3', 'Category 4', 'Category 5', 'Category 6']
    fallback_department = ['Registrar', 'SGS', 'SOB', 'SCJ', 'SOA', 'SOE', 'SOL', 'Administration', 'OSA', 'SESO',
                       'Accounting', 'HR', 'Cashier', 'OTP', 'Marketing', 'SHS', 'Quacro', 'Library', 'MIS', 'GenServ']
    fallback_account_type = ['user', 'admin']
    fallback_status = ['active', 'assigned', 'for repair', 'for disposal']

    c = get_cursor()
    c.execute("SELECT employee_id, CONCAT(last_name, ', ', first_name) AS full_name FROM employees")
    employees = c.fetchall()
    employee_options = ['-- None --'] + [f"{emp[1]}" for emp in employees]
    c.close()
    c = get_cursor()
    c.execute("SELECT id, subcategory FROM subcategories ORDER BY subcategory ASC")
    subcategory_options = c.fetchall()  # List of (id, name)
    c.close()
    return {
        'subcategory': subcategory_options,
        'department': load_options('department.txt', fallback_department),
        'Assigned To': employee_options,
        'account_type': load_options('account_type.txt', fallback_account_type),
        'status': load_options('status.txt', fallback_status)
    }

def get_items_columns():
    return [
        'item id', 'item name', 'subcategory', 'category',
        'brand name', 'description', 'specification', 'Assigned To', 'department', 'status', 'last_updated'
    ]

def get_items_query():
    return """
        SELECT i.item_id AS 'item id', 
        i.item_name AS 'item name', subcat.subcategory, cat.category AS 'category',
        i.brand_name AS 'brand name', i.description, i.specification, CONCAT(e.last_name, ', ', e.first_name) AS 'Assigned To', e.department, i.status, i.last_updated
        FROM items i
        LEFT JOIN employees e ON i.employee = e.employee_id
        LEFT JOIN subcategories subcat ON i.subcategory = subcat.id
        LEFT JOIN items_categories cat ON subcat.category_id = cat.id
    """

def get_filters(table_name):
    c = get_cursor()

    # Fetch the column names for the table
    if table_name == 'items':
        columns = get_items_columns()
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]

    # Improved filter collection to handle multiple values and spaces
    filters = {}
    for column in columns:
        if column != 'password':
            # Handle both + and %20 encoded spaces
            url_encoded_column = column.replace(' ', '+')
            values = request.args.getlist(url_encoded_column)
            if not values:
                url_encoded_column = column.replace(' ', '%20')
                values = request.args.getlist(url_encoded_column)
            
            values = [v.strip() for v in values if v.strip()]
            if values:
                filters[column] = ' '.join(values) if len(values) > 1 else values[0]


    
    return filters

def filter_table(table_name, cursor, page=1, per_page=15):
    if not is_valid_table(table_name):
        abort(400)

    # Get the search term from the query string
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip() if table_name == 'items' else None

    if table_name == 'items':
        columns = get_items_columns()
    else:
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in cursor.fetchall()]

    where_clauses = []
    filter_values = []

    # Global search (all columns)
    if search_term:
        or_clauses = []
        for col in columns:
            if col == 'password':
                continue
            if table_name in ('items', 'items_disposal'):
                if col == "Assigned To":
                    or_clauses.append("CONCAT(e.last_name, ', ', e.first_name) LIKE %s")
                else:
                    or_clauses.append(f"i.`{col}` LIKE %s")
            else:
                or_clauses.append(f"`{col}` LIKE %s")
            filter_values.append(f"%{search_term}%")
        if or_clauses:
            where_clauses.append(f"({' OR '.join(or_clauses)})")

    # Status filter for items table
    if table_name == 'items' and status_filter:
        where_clauses.append("i.status = %s")
        filter_values.append(status_filter)

    # Build the base query
    if table_name in ('items', 'items_disposal'):
        sql_query = get_items_query()
        count_query = "SELECT COUNT(*) FROM items i LEFT JOIN employees e ON i.employee = e.employee_id"
    else:
        sql_query = f"SELECT * FROM `{table_name}`"
        count_query = f"SELECT COUNT(*) FROM `{table_name}`"

    # Add WHERE conditions if any
    if where_clauses:
        sql_query += f" WHERE {' AND '.join(where_clauses)}"
        count_query += f" WHERE {' AND '.join(where_clauses)}"

    # Add sorting
    sort_column = request.args.get('sort_column')
    sort_direction = request.args.get('sort_direction', 'asc')
    if sort_column and sort_direction.lower() in ['asc', 'desc']:
        if table_name in ('items', 'items_disposal'):
            if sort_column == "Assigned To":
                sql_query += f" ORDER BY CONCAT(e.last_name, ', ', e.first_name) {sort_direction}"
            else:
                sql_query += f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            sql_query += f" ORDER BY `{sort_column}` {sort_direction}"

    # Add pagination
    offset = (page - 1) * per_page
    sql_query += f" LIMIT %s OFFSET %s"
    query_values = tuple(filter_values) + (per_page, offset)

    try:
        # Get total count for pagination
        cursor.execute(count_query, tuple(filter_values))
        total_items = cursor.fetchone()[0]
        # Get paginated results
        cursor.execute(sql_query, query_values)
        filters = {'search': search_term}
        if table_name == 'items':
            filters['status'] = status_filter
        return cursor.fetchall(), columns, filters, total_items
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        filters = {'search': search_term}
        if table_name == 'items':
            filters['status'] = status_filter
        return [], columns, filters, 0
    
def get_preserved_args():
    """Returns current filters and pagination as query string"""
    preserved_args = request.args.copy()
    # Remove these if you don't want them carried over
    preserved_args.pop('_flashes', None) 
    preserved_args.pop('csrf_token', None)
    return preserved_args

def preserve_current_entries(columns):
    """Preserve current entries in the form data"""
    current_datetime = datetime.datetime.now()

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
    return entry

def calculate_column_widths(items, columns):
    """Calculate relative column widths based on content"""
    if not items:
        return {col: 1 for col in columns}
    
    sample_rows = items[:10]
    width_factors = {}
    max_content_lengths = {}
    
    for col_idx, column in enumerate(columns):
        max_len = len(column)  # Start with header length
        max_content_length = 0
        
        for row in sample_rows:
            value = str(row[col_idx] if row[col_idx] is not None else '')
            max_len = max(max_len, len(value))
            # Count words rather than characters for better width estimation
            max_content_length = max(max_content_length, len(value.split()))
        
        # Dynamic width calculation
        if max_content_length > 15:  # Long text content
            width_factors[column] = 2.5
        elif max_content_length > 8:
            width_factors[column] = 1.5
        else:
            width_factors[column] = 1
    
    return width_factors

def get_item_assignment_history(item_id):
    """Return assignment history for an item, ordered by assigned_date desc."""
    c = get_cursor()
    c.execute(
        """
        SELECT h.item_id, CONCAT(e.last_name, ', ', e.first_name) AS full_name, h.assigned_date, h.removed_date
        FROM item_assignment_history h
        LEFT JOIN employees e ON h.employee_id = e.employee_id
        WHERE h.item_id = %s
        ORDER BY h.assigned_date DESC
        """,
        (item_id,)
    )
    history = c.fetchall()
    c.close()
    return history

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
    
    # Prepare for ID generation (must be before row loop)
    id_column = next((col for col in db_columns if col == 'id' or col.endswith('_id')), None)
    next_num = None
    if id_column:
        c.execute(f"SELECT MAX({id_column}) AS max_id FROM `{table_name}`")
        max_id = c.fetchone()[0]
        if table_name == 'items':
            if max_id is None:
                next_num = 1
            elif isinstance(max_id, str) and max_id.startswith('MLQU-'):
                num_part = max_id.split('-')[-1]
                next_num = int(num_part) + 1 if num_part.isdigit() else 1
            else:
                next_num = 1
        else:
            next_num = (int(max_id) if max_id is not None else 0) + 1

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