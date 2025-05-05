from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

import datetime

from invemp.auth import login_required
from invemp.dashboard_helpers import (
    is_valid_table, get_filters, get_tables, calculate_column_widths, get_items_columns, get_items_query
    )
from invemp.db import get_cursor

import re
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

    # Pagination setup
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    per_page = 15
    offset = (page - 1) * per_page

    filters = get_filters(table_name)
    where_clauses = []
    filter_values = []
    
    # Build WHERE clause from filters
    for col, value in filters.items():
        if table_name in ('items', 'items_disposal') and col == "Assigned To":
            where_clauses.append("e.name LIKE %s")
        elif table_name in ('items', 'items_disposal'):
            where_clauses.append(f"i.`{col}` LIKE %s")
        else:
            where_clauses.append(f"`{col}` LIKE %s")
        filter_values.append(f"%{value}%")
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # Sorting (optional)
    sort_column = request.args.get('sort_column')
    sort_direction = request.args.get('sort_direction', 'asc')
    order_sql = ""
    if sort_column and sort_direction.lower() in ['asc', 'desc']:
        if table_name in ('items', 'items_disposal'):
            if sort_column == "Assigned To":
                order_sql = f" ORDER BY e.name {sort_direction}"
            else:
                order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            order_sql = f" ORDER BY `{sort_column}` {sort_direction}"
    
    if table_name == 'items':
        query = get_items_query()
        query = re.sub(r'\s+LIMIT\s+\d+\s*$', '', query, flags=re.IGNORECASE)
        paginated_query = f"{query}{where_sql}{order_sql} LIMIT %s OFFSET %s"
        c = get_cursor()
        c.execute(paginated_query, (*filter_values, per_page, offset))
        items = c.fetchall()
        columns = [column[0] for column in c.description if column[0] != 'status']
        # Remove the 'status' value from each row
        status_idx = [i for i, col in enumerate(c.description) if col[0] == 'status']
        if status_idx:
            idx = status_idx[0]
            items = [row[:idx] + row[idx+1:] for row in items]

        # Get total count for pagination
        count_query = f"SELECT COUNT(*) FROM items LEFT JOIN employees e ON items.employee = e.employee_id" + (where_sql if where_sql else "")
        c.execute(count_query, tuple(filter_values))
        total = c.fetchone()[0]
        c.close()

    elif table_name == 'user_accounts':
        c = get_cursor()
        query = f"SELECT id, username, account_type FROM `{table_name}` LIMIT 100"
        columns = [column[0] for column in c.description]
        items = c.fetchall()
        c.close()
    else:
        # Generic query for other tables
        c.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        items = c.fetchall()
        columns = [column[0] for column in c.description]
        c.close()

    total_pages = (total + per_page - 1) // per_page
    args = request.args.to_dict()

    
    return render_template('dashboard/index.html', items=items, columns=columns, 
                           table_name=table_name, tables = get_tables(), 
                           filters = filters, page = page, total_pages = total_pages,
                           args = args, is_index = True)

@bp.route('/<table_name>/filter', methods=('GET', 'POST'))
@login_required
def filter_items(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()

    # Pagination setup
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    per_page = 15
    offset = (page - 1) * per_page

    # Fetch the column names for the table
    if table_name in ('items', 'items_disposal'):
        columns = get_items_columns()
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]

    # Get filter criteria
    filters = {}
    for column in columns:
        url_encoded_column = column.replace(' ', '+')
        values = request.args.getlist(url_encoded_column)
        if not values:
            url_encoded_column = column.replace(' ', '%20')
            values = request.args.getlist(url_encoded_column)
        values = [v.strip() for v in values if v.strip()]
        if values:
            filters[column] = ' '.join(values) if len(values) > 1 else values[0]

    # Build the WHERE clause
    where_clauses = []
    filter_values = []
    for col, value in filters.items():
        if col == "Assigned To":
            where_clauses.append("e.name LIKE %s")
        else:
            escaped_col = f"i.`{col}`" if table_name in ('items', 'items_disposal') else f"`{col}`"
            where_clauses.append(f"{escaped_col} LIKE %s")
        filter_values.append(f"%{value}%")

    # Build the base query
    if table_name in ('items', 'items_disposal'):
        sql_query = get_items_query()
        sql_query = re.sub(r'\s+LIMIT\s+\d+\s*$', '', sql_query, flags=re.IGNORECASE)
    else:
        sql_query = f"SELECT * FROM `{table_name}`"

    # Add WHERE clause if we have filters
    if where_clauses:
        sql_query += f" WHERE {' AND '.join(where_clauses)}"

    # Add ORDER BY if needed (optional)
    sort_column = request.args.get('sort_column')
    sort_direction = request.args.get('sort_direction', 'asc')
    order_sql = ""
    if sort_column and sort_direction.lower() in ['asc', 'desc']:
        if table_name in ('items', 'items_disposal'):
            if sort_column == "Assigned To":
                order_sql = f" ORDER BY e.name {sort_direction}"
            else:
                order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            order_sql = f" ORDER BY `{sort_column}` {sort_direction}"
    sql_query += order_sql

    # Add LIMIT/OFFSET for pagination
    paginated_query = f"{sql_query} LIMIT %s OFFSET %s"

    # Debug output
    print("Generated SQL:", paginated_query)
    print("Parameters:", filter_values + [per_page, offset])

    # Execute paginated query
    try:
        c.execute(paginated_query, tuple(filter_values) + (per_page, offset))
        items = c.fetchall()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        print(f"Query: {paginated_query}")
        print(f"Params: {filter_values + [per_page, offset]}")
        flash("An error occurred while filtering items", "error")
        items = []
    # Get total count for pagination
    count_query = f"SELECT COUNT(*) FROM {('items LEFT JOIN employees e ON items.employee = e.employee_id') if table_name in ('items', 'items_disposal') else table_name}"
    if where_clauses:
        count_query += f" WHERE {' AND '.join(where_clauses)}"
    try:
        c.execute(count_query, tuple(filter_values))
        total = c.fetchone()[0]
    except Exception as e:
        total = 0
    finally:
        c.close()

    total_pages = (total + per_page - 1) // per_page
    args = request.args.to_dict()
    args.pop('page', None)

    return render_template('dashboard/index.html',
                         items=items,
                         columns=columns,
                         table_name=table_name,
                         tables=get_tables(),
                         filters=filters,
                         page=page,
                         total_pages=total_pages,
                         args=args,
                         is_index=True)

@bp.route('/<table_name>/convert_pdf')
@login_required
def convert_pdf(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    request_args = request.args

    # Fetch the column names for the table
    if table_name in ('items', 'items_disposal'):
        columns = get_items_columns()
        base_query = get_items_query()
    else:
        c.execute(f"DESCRIBE `{table_name}`")
        columns = [row[0] for row in c.fetchall()]
        base_query = f"SELECT * FROM `{table_name}`"

    # --- Handle Filters ---
    where_clauses = []
    filter_values = []
    
    # Process each possible filter parameter
    for column in columns:
        # Handle both single values and lists of values
        values = request_args.getlist(column) or ([request_args[column]] if column in request_args else [])
        values = [v for v in values if v.strip()]  # Filter out empty values
        
        if values:
            # Join multiple values with spaces for LIKE matching
            search_value = ' '.join(values)
            
            if table_name in ('items', 'items_disposal') and column == "Assigned To":
                where_clauses.append("e.name LIKE %s")
            elif table_name in ('items', 'items_disposal'):
                where_clauses.append(f"i.`{column}` LIKE %s")
            else:
                where_clauses.append(f"`{column}` LIKE %s")
                
            filter_values.append(f"%{search_value}%")
    
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # --- Handle Sorting ---
    sort_column = request_args.get('sort_column') or request_args.get('column')
    sort_direction = request_args.get('sort_direction', 'asc')
    
    order_sql = ""
    if sort_column and sort_column in columns and sort_direction.lower() in ['asc', 'desc']:
        if table_name in ('items', 'items_disposal'):
            if sort_column == "Assigned To":
                order_sql = f" ORDER BY e.name {sort_direction}"
            else:
                order_sql = f" ORDER BY i.`{sort_column}` {sort_direction}"
        else:
            order_sql = f" ORDER BY `{sort_column}` {sort_direction}"

    # --- Final Query ---
    sql_query = re.sub(r'\s+LIMIT\s+\d+\s*$', '', base_query, flags=re.IGNORECASE) + where_sql + order_sql

    # Execute the query
    try:
        c.execute(sql_query, tuple(filter_values))
        items = c.fetchall()
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        print(f"Query: {sql_query}")
        print(f"Params: {filter_values}")
        flash("Error generating PDF", "error")
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    finally:
        c.close()

    html = render_template(
        'pdf_template.html',
        items=items,
        columns=columns,
        table_name=table_name,
        current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        column_widths=calculate_column_widths(items, columns),
        zip=zip,
        filters=request_args  # Pass filters for header display
    )

    # Generate PDF
    pdf = HTML(
        string=html,
        base_url=request.base_url
    ).write_pdf(stylesheets=[
        CSS(string='''
            @page { 
                size: A4 landscape;
                margin: 1cm; 
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 8pt;
                }
            }
            body { 
                font-family: Arial; 
                font-size: 9pt;
                line-height: 1.3;
            }
            .header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }
            th, td {
                padding: 4px;
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            .filters {
                font-size: 8pt;
                margin-bottom: 5px;
                color: #555;
            }
            ''')
    ])

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={table_name}_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    return response

@bp.route('/<table_name>/convert_pdf_qr')
@login_required
def convert_pdf_qr(table_name):
    if not is_valid_table(table_name):
        abort(400)
    c = get_cursor()
    request_args = request.args.to_dict()

    # Columns and base query (same as your convert_pdf)
    if table_name == 'items':
        columns = get_items_columns()
        base_query = get_items_query()
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