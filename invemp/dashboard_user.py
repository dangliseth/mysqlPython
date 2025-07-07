from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

import datetime

from invemp.auth import login_required
from invemp.dashboard_helpers import (
    is_valid_table, get_tables, calculate_column_widths, get_items_columns, get_items_query,
    filter_table, get_preserved_args
    )
from invemp.db import get_cursor

import qrcode
from fpdf import FPDF
from weasyprint import CSS, HTML


bp = Blueprint('dashboard_user', __name__)

@bp.route('/', defaults={'table_name': 'employees'})
@bp.route('/<table_name>')
@login_required
def index(table_name):
    # Check for admin access
    if g.user[3] != 'admin' and table_name != 'items':
        return redirect(url_for('dashboard_user.index', table_name='items'))

    # Pagination setup
    try:
        page = int(request.args.get('page', 1))
        page = max(page, 1)  # Ensure page is at least 1
    except ValueError:
        page = 1
    per_page = 15

    # Get filtered results using the helper
    c = get_cursor()
    try:
        # Get filtered items and columns, and total filtered count
        filtered_items, columns, filters, total_items = filter_table(table_name, c, page=page, per_page=per_page)
        total_pages = (total_items + per_page - 1) // per_page
    finally:
        c.close()

    # For items table, use the display-friendly column names
    display_columns = get_items_columns() if table_name == 'items' else columns
    pagination_args = request.args.copy()
    if 'page' in pagination_args:
        del pagination_args['page']
    merged_args = dict(pagination_args)
    merged_args.update(filters)

    # AJAX partial rendering for table and pagination
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('dashboard/_table.html',
                             items=filtered_items,
                             columns=display_columns,
                             table_name=table_name,
                             page=page,
                             total_pages=total_pages,
                             merged_args=merged_args,
                             zip=zip)

    return render_template('dashboard/index.html',
                         items=filtered_items,
                         columns=display_columns,
                         table_name=table_name,
                         tables=get_tables(),
                         filters=filters,
                         page=page,
                         zip = zip,
                         total_pages=total_pages,
                         pagination_args=pagination_args,  # Pass filter args without page
                         total_items=total_items,
                         args=request.args.to_dict(),
                         is_index=True)

@bp.route('/<table_name>/<id>')
@login_required
def view_details(table_name, id):
    id_column = None
    args = get_preserved_args()
    c = get_cursor()
    c.execute(f'DESCRIBE {table_name}')
    description = c.fetchall()
    columns = [row[0] for row in description]
    c.close()
    for column in columns:
        if column == 'id' or column.endswith('_id'):
            id_column = column
            break
    if table_name == 'items':
        columns = [col if col != 'employee' else 'Assigned To' for col in columns]
        details_query = f'''
        SELECT i.*, s.subcategory, CONCAT(e.last_name, ', ', e.first_name) AS "Assigned To" 
        FROM {table_name} i 
        LEFT JOIN subcategories s ON i.subcategory = s.id
        LEFT JOIN employees e ON i.employee = e.employee_id
        WHERE i.{id_column} = %s
        '''
    else:
        details_query = f"""
        SELECT * FROM {table_name} WHERE {id_column} = %s
        """

    try:
        c = get_cursor()
        c.execute(details_query, (id,))
        details = c.fetchone()
    except Exception as e:
        flash(f"Error fetching entry details: {e}", 'error')
        return redirect(url_for('dashboard_user.index', table_name=table_name))
    finally:
        c.close()

    return render_template('dashboard/view_details.html',
                            entry=details,
                            table_name=table_name,
                            columns=columns,
                            id_column=id_column,
                            id=id,
                            args=args)
        

@bp.route('/<table_name>/convert_pdf')
@login_required
def convert_pdf(table_name):
    if not is_valid_table(table_name):
        abort(400)
    # Get current page and per_page from request (default to 1 and 15)
    try:
        page = int(request.args.get('page', 1))
        page = max(page, 1)
    except ValueError:
        page = 1
    per_page = 15
    c = get_cursor()
    try:
        filtered_items, columns, filters, total_items = filter_table(table_name, c, page=page, per_page=per_page)
    finally:
        c.close()

    # --- PDF COLUMN/ROW TRANSFORM FOR 'items' TABLE ---
    if table_name == 'items':
        # Build new columns: replace 'item_name' and 'Assigned To' with combined columns, remove 'category' and 'department'
        new_columns = []
        for col in columns:
            if col == 'item_name':
                new_columns.append('Item (Category)')
            elif col == 'Assigned To':
                new_columns.append('Assigned To (Department)')
            elif col in ('category', 'department'):
                continue
            else:
                new_columns.append(col)
        # Build new rows
        new_items = []
        for row in filtered_items:
            row = list(row)
            new_row = []
            for idx, col in enumerate(columns):
                if col == 'item_name':
                    item_name = row[columns.index('item_name')]
                    category = row[columns.index('category')]
                    combined = f"{item_name}\n({category})" if category else str(item_name)
                    new_row.append(combined)
                elif col == 'Assigned To':
                    assigned_to = row[columns.index('Assigned To')]
                    department = row[columns.index('department')]
                    combined = f"{assigned_to}\n({department})" if department else str(assigned_to)
                    new_row.append(combined)
                elif col in ('category', 'department'):
                    continue
                else:
                    new_row.append(row[idx])
            new_items.append(new_row)
        columns = new_columns
        filtered_items = new_items

    html = render_template(
        'pdf_template.html',
        items=filtered_items,
        columns=columns,
        table_name=table_name,
        current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        column_widths=calculate_column_widths(filtered_items, columns),
        zip=zip,
        filters=filters,  # Pass filters for header display
        total_items=len(filtered_items)  # Add total number of items
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
            word-wrap: break-word;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #ddd;
            text-align: left;
        }
        td {
            padding: 4px;
            border: 1px solid #ddd;
            vertical-align: top;
            word-break: break-word;
        }
        .filters {
            font-size: 8pt;
            margin-bottom: 5px;
            color: #555;
        }
        tr {
            page-break-inside: avoid;
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
    # Get current page and per_page from request (default to 1 and 15)
    try:
        page = int(request.args.get('page', 1))
        page = max(page, 1)
    except ValueError:
        page = 1
    per_page = 15
    c = get_cursor()
    try:
        filtered_items, columns, filters, total_items = filter_table(table_name, c, page=page, per_page=per_page)
    finally:
        c.close()

    if table_name == 'items' or table_name == 'items_disposal':
        qr_columns = ['item_id', 'item_name', 'serial_number']  # Change as needed
    else:
        qr_columns = columns

    # Map column names to their index in the row
    col_indices = {col: idx for idx, col in enumerate(columns)}

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Add header with generation date, time, and total items
    generated_str = f"Generated on {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | Total items: {len(filtered_items)}"
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
    for idx, row in enumerate(filtered_items):
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