from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

import datetime

from invemp.auth import login_required
from invemp.dashboard_helpers import is_valid_table, get_filters, get_tables, calculate_column_widths
from invemp.db import get_cursor

import qrcode
from fpdf import FPDF
from weasyprint import CSS, HTML

bp = Blueprint('dashboard_user', __name__)

@bp.route('/', defaults={'table_name': 'items'})
@bp.route('/<table_name>')
@login_required
def index(table_name):
    # check for admin access
    if g.user[3] != 'admin' and table_name != 'items':
        flash("You do not have permission to access this table.")
        return redirect(url_for('dashboard_user.index', table_name))
    
    if not is_valid_table(table_name):
        abort(400)

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
    elif table_name == 'user_accounts':
        c.execute(f"SELECT id, username, account_type FROM `{table_name}` LIMIT 100")
        columns = [column[0] for column in c.description if column != 'password']
        items = c.fetchall()
    else:
        # Generic query for other tables
        c.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        items = c.fetchall()
        columns = [column[0] for column in c.description]
    c.close()

    tables = get_tables()
    filters = get_filters(table_name)
    return render_template('dashboard/index.html', items=items, columns=columns, 
                           table_name=table_name, tables=tables, filters = filters, is_index = True)

@bp.route('/<table_name>/filter', methods=('GET', 'POST'))
@login_required
def filter_items(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()

    # Fetch the column names for the table
    if table_name == 'items' or table_name == 'items_disposal':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                   'comment', 'Assigned To', 'department', 'last_updated']
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]

    # Get filter criteria from the request
    filters = {column: request.args.get(column) for column in columns if request.args.get(column)}

    # Build the WHERE clause dynamically
    where_clauses = []
    filter_values = []
    for col, value in filters.items():
        if col == "Assigned To":
            where_clauses.append("e.name LIKE %s")
        else:
            where_clauses.append(f"i.`{col}` LIKE %s" if table_name == 'items' or table_name == 'items_disposal' else f"`{col}` LIKE %s")
        filter_values.append(f"%{value}%")
    where_clause = " AND ".join(where_clauses)
    if table_name == 'items' or table_name == 'items_disposal':
        sql_query = f"""
            SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
            i.comment, e.name AS 'Assigned To', i.department, i.last_updated
            FROM items i
            LEFT JOIN employees e ON i.employee = e.employee_id
        """
    else:
        sql_query = f"SELECT * FROM `{table_name}`"
    if where_clause:
        sql_query += f" WHERE {where_clause}"
    sql_query += " LIMIT 100"

    filter_values = [f"%{value}%" for value in filters.values()]

    # Execute the query with filter values
    c.execute(sql_query, tuple(filter_values))
    items = c.fetchall()
    c.close()

    tables = get_tables()
    return render_template('dashboard/index.html', items=items, columns=columns, table_name=table_name, 
                           tables=tables, filters=filters, is_index = True)

@bp.route('/<table_name>/convert_pdf')
@login_required
def convert_pdf(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    request_args = request.args.to_dict()


    # Fetch the column names for the table
    if table_name == 'items':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                    'comment', 'Assigned To', 'department', 'last_updated']
        base_query = """
            SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
            i.comment, e.name AS 'Assigned To', i.department, i.last_updated
            FROM items i
            LEFT JOIN employees e ON i.employee = e.employee_id
        """
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]
        base_query = f"SELECT * FROM `{table_name}`"

    # --- Handle Filters ---
    where_clauses = []
    filter_values = []
    
    # Process each possible filter parameter
    for column in columns:
        if column in request_args and request_args[column]:
            value = request_args[column]
            if table_name == 'items' and column == "Assigned To":
                where_clauses.append("e.name LIKE %s")
            elif table_name == 'items':
                where_clauses.append(f"i.`{column}` LIKE %s")
            else:
                where_clauses.append(f"`{column}` LIKE %s")
            filter_values.append(f"%{value}%")
    
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # --- Handle Sorting ---
    sort_column = request_args.get('sort_column') or request_args.get('column')
    sort_direction = request_args.get('sort_direction', 'asc')
    
    order_sql = ""
    if sort_column and sort_column in columns and sort_direction.lower() in ['asc', 'desc']:
        if table_name == 'items':
            if sort_column == "Assigned To":
                order_sql = f" ORDER BY e.name {sort_direction}"
            else:
                order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            order_sql = f" ORDER BY `{sort_column}` {sort_direction}"

    # --- Final Query ---
    sql_query = base_query + where_sql + order_sql

    # Execute the query
    c.execute(sql_query, tuple(filter_values))
    items = c.fetchall()
    c.close()

    html = render_template(
        'pdf_template.html',  # Create a new template specifically for PDF
        items=items,
        columns=columns,
        table_name=table_name,
        current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        column_widths=calculate_column_widths(items, columns),
        zip = zip
    )

    # Generate PDF with proper CSS
    pdf = HTML(
        string=html,
        base_url=request.base_url  # Important for static files
    ).write_pdf(stylesheets=[
        CSS(string='''
            @page { 
            size: A4 landscape;  /* Landscape often works better for wide tables */
            margin: 1cm; 
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 8pt;
            }
            }
            body { 
                font-family: Arial; 
                font-size: 9pt;  /* Slightly smaller font */
                line-height: 1.3;
            }
            h1 { 
                color: #333; 
                text-align: center;
                margin-bottom: 0.5cm;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;  /* Essential for column control */
                display: flex
                flex-direction: row
            }
            th {
                background-color: #f2f2f2;
                text-align: left;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            td {
                padding: 4px;
                border: 1px solid #ddd;
                vertical-align: top;  /* Align content to top */
            }
            .timestamp {
                font-size: 8pt;       /* Smaller font for timestamps */
            }
            ''')
    ])

    # Output PDF as a downloadable file
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={table_name}_report.pdf'
    return response

@bp.route('/<table_name>/convert_pdf_qr')
@login_required
def convert_pdf_qr(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    request_args = request.args.to_dict()

    # Columns and base query (same as your convert_pdf)
    if table_name == 'items' or table_name == 'items_disposal':
        columns = ['item_id', 'serial_number', 'item_name', 'category', 'description', 
                'comment', 'Assigned To', 'department', 'last_updated']
        base_query = """
            SELECT i.item_id, i.serial_number, i.item_name, i.category, i.description, 
            i.comment, e.name AS 'Assigned To', i.department, i.last_updated
            FROM items i
            LEFT JOIN employees e ON i.employee = e.employee_id
        """
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]
        base_query = f"SELECT * FROM `{table_name}`"

    # --- Handle Filters ---
    where_clauses = []
    filter_values = []
    for column in columns:
        if column in request_args and request_args[column]:
            value = request_args[column]
            if table_name in ['items', 'items_disposal']:
                if column == "Assigned To":
                    where_clauses.append("e.name LIKE %s")
                else:
                    where_clauses.append(f"i.`{column}` LIKE %s")
            else:
                where_clauses.append(f"`{column}` LIKE %s")
            filter_values.append(f"%{value}%")
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # --- Handle Sorting ---
    sort_column = request_args.get('sort_column') or request_args.get('column')
    sort_direction = request_args.get('sort_direction', 'asc')
    order_sql = ""
    if sort_column and sort_column in columns and sort_direction.lower() in ['asc', 'desc']:
        if table_name in ['items', 'items_disposal']:
            if sort_column == "Assigned To":
                order_sql = f" ORDER BY e.name {sort_direction}"
            else:
                order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            order_sql = f" ORDER BY `{sort_column}` {sort_direction}"

    sql_query = base_query + where_sql + order_sql

    c.execute(sql_query, tuple(filter_values))
    items = c.fetchall()
    c.close()

    if table_name == 'items' or table_name == 'items_disposal':
        # --- Only include these columns in the QR code ---
        qr_columns = ['item_id', 'item_name', 'serial_number']  # Change as needed
    else:
        qr_columns = columns

    # Map column names to their index in the row
    col_indices = {col: idx for idx, col in enumerate(columns)}

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Add header with generation date and time
    generated_str = f"Generated on {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    pdf.cell(0, 10, generated_str, ln=1, align='C')

    page_width = 190
    qr_width = 25
    qr_height = 25
    spacing = 10
    max_per_row = page_width // (qr_width + spacing)
    x_start = 10
    y_start = 20
    x = x_start
    y = y_start

    import tempfile
    for idx, row in enumerate(items):
        # Build QR data string with only the selected columns
        qr_data = "\n".join(f"{col}: {row[col_indices[col]]}" for col in qr_columns)
        qr_img = qrcode.make(qr_data)
        # Save QR image to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            qr_img.save(tmp_file, format='PNG')
            tmp_file_path = tmp_file.name
        pdf.image(tmp_file_path, x=x, y=y, w=qr_width, h=qr_height, type='PNG')
        pdf.set_xy(x, y + qr_height)
        label_col = 'item_id' if 'item_id' in col_indices else columns[0]
        pdf.cell(qr_width, 5, f"{row[col_indices[label_col]]}", 0, 0, "C")

        x += qr_width + spacing
        if (idx + 1) % max_per_row == 0:
            x = x_start
            y += qr_height + 15
        if y + qr_height + 15 > 277:
            pdf.add_page()
            x = x_start
            y = y_start

    # Optionally, clean up temp files after PDF generation
    import glob, os
    for tmp_file in glob.glob(os.path.join(tempfile.gettempdir(), "tmp*.png")):
        try:
            os.remove(tmp_file)
        except Exception:
            pass

    pdf_bytes = pdf.output(dest='S').encode('latin1')

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={table_name}_qr_report.pdf'
    return response