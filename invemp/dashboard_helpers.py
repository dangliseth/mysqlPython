from flask import (
    request
)

from invemp.db import get_cursor
from werkzeug.exceptions import abort

import datetime


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
    c = get_cursor()
    
    # Get all employees
    c.execute("SELECT employee_id, name FROM employees")
    employees = c.fetchall()
    
    # Format as list of "ID - Name" strings
    employee_options = ['-- None --'] + [f"{emp[1]}" for emp in employees]
    c.close()
    return {
        'category': ['Computer', 'Category 2', 'Category 3', 'Category 4', 'Category 5', 'Category 6'],
        'department': ['Registrar', 'SGS', 'SOB', 'SCJ', 'SOA', 'SOE', 'SOL', 'Administration', 'OSA', 'SESO',
                       'Accounting', 'HR', 'Cashier', 'OTP', 'Marketing', 'SHS', 'Quacro', 'Library', 'MIS', 'GenServ'],
        'Assigned To': employee_options,
        'account_type': ['user', 'admin'],
        'status': ['active', 'assigned', 'for repair', 'for disposal']
    }

def get_items_columns():
    return [
        'item_id', 'serial_number', 'item_name', 'category', 'description',
        'comment', 'Assigned To', 'department', 'status', 'last_updated'
    ]

def get_items_query():
    return """
        SELECT i.item_id AS 'item id', i.serial_number AS 'serial number', 
        i.item_name AS 'item name', i.category, i.description, 
        i.comment, e.name AS 'Assigned To', i.department, i.status, i.last_updated
        FROM items i
        LEFT JOIN employees e ON i.employee = e.employee_id
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
                    or_clauses.append("e.name LIKE %s")
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
                sql_query += f" ORDER BY e.name {sort_direction}"
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
        SELECT h.item_id, e.name, h.assigned_date, h.removed_date
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