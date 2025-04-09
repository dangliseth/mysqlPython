from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from invemp.auth import login_required
from invemp.db import get_cursor

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    c = get_cursor()
    c.execute('SHOW TABLES')
    tables = [table[0] for table in c.fetchall()]

    return render_template('dashboard/index.html', tables=tables)