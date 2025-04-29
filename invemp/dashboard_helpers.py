from flask import (
    request, flash
)

from invemp.db import get_cursor

def get_pagination_params(request_args, total_rows, per_page=20):
    page = int(request_args.get('page', 1))
    if page < 1:
        page = 1
    total_pages = (total_rows + per_page - 1) // per_page
    offset = (page - 1) * per_page
    return page, per_page, offset, total_pages

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