from flask import (
    request, flash
)

from invemp.db import get_cursor
from werkzeug.exceptions import abort


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

def filter_table(table_name, cursor):
    if not is_valid_table(table_name):
        abort(400)

    filters = get_filters(table_name)
    
    if table_name == 'items':
        columns = get_items_columns()
    else:
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in cursor.fetchall()]

    where_clauses = []
    filter_values = []
    
    for col, values in filters.items():
        if not isinstance(values, list):
            values = [values]
            
        # Handle special case for "Assigned To"
        if col == "Assigned To":
            col_expr = "e.name"
        else:
            col_expr = f"i.`{col}`" if table_name in ('items', 'items_disposal') else f"`{col}`"
        
        # Create OR conditions for multiple values of the same column
        column_clauses = []
        for value in values:
            column_clauses.append(f"{col_expr} LIKE %s")
            filter_values.append(f"%{value}%")
        
        # Combine with OR for the same column, then add to WHERE clauses
        where_clauses.append(f"({' OR '.join(column_clauses)})")

    # Build the base query
    if table_name in ('items', 'items_disposal'):
        sql_query = get_items_query()
    else:
        sql_query = f"SELECT * FROM `{table_name}`"

    # Add WHERE conditions if any filters exist
    if where_clauses:
        sql_query += f" WHERE {' AND '.join(where_clauses)}"

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

    try:
        cursor.execute(sql_query, tuple(filter_values))
        return cursor.fetchall(), columns, filters
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        return [], columns, filters


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