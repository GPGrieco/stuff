import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from .. import db
from ..models import Maintenance

bp = Blueprint('maintenance', __name__)

@bp.route('/')
def index():
    logs = Maintenance.query.order_by(Maintenance.date_reported.desc()).all()
    return render_template('maintenance/index.html', logs=logs)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        photo = request.files.get('photo')
        filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'maintenance', filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            photo.save(path)
        log = Maintenance(equipment=request.form['equipment'], issue=request.form['issue'], done=('done' in request.form), notes=request.form['notes'], photo=filename)
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('maintenance.index'))
    return render_template('maintenance/add.html')
