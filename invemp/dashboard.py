from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from invemp.auth import login_required, admin_required
from invemp.db import get_cursor

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@admin_required
def index():
    c = get_cursor()
    c.execute('SHOW TABLES')
    tables = [table[0] for table in c.fetchall()]
    c.close()

    return render_template('dashboard/index.html', tables=tables)

@bp.route('/view_table/<table_name>')
@login_required
def view_table(table_name):
    # check for admin access
    if g.user[3] != 'admin' and table_name != 'items':
        flash("You do not have permission to access this table.")
        return redirect(url_for('dashboard.index'))
    

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
    else:
        # Generic query for other tables
        c.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        items = c.fetchall()
        columns = [column[0] for column in c.description]
    c.close()
    return render_template('dashboard/view_table.html', items=items, columns=columns, table_name=table_name)

def get_item(item_id):
    c = get_cursor()
    c.execute('SELECT * FROM items WHERE item_id = %s', (item_id,))
    item = c.fetchone()
    c.close()
    return item

@bp.route('/view_table/<table_name>/create', methods=('GET', 'POST'))
@admin_required
def create(table_name):
    c = get_cursor()

    c.execute(f"DESCRIBE `{table_name}`")
    columns = [row[0] for row in c.fetchall()]
    c.close()

    if request.method == 'POST':
        values = [request.form.get(column) for column in columns]
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO '{table_name}' ({', '.join(columns)}) VALUES ({placeholders})"

        c = get_cursor()
        c.execute(query, values)
        c.connection.commit()
        c.close()

        flash(f"Successfully created new {table_name[:-1]}")
        return redirect(url_for('dashboard.view_table', table_name=table_name))
    return render_template('dashboard/create.html', table_name=table_name, columns=columns)