import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from .. import db
from ..models import Patrol

bp = Blueprint('patrols', __name__)

@bp.route('/')
def index():
    patrols = Patrol.query.order_by(Patrol.date.desc()).all()
    return render_template('patrols/index.html', patrols=patrols)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        photo = request.files.get('photo')
        filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'patrols', filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            photo.save(path)
        patrol = Patrol(area=request.form['area'], notes=request.form['notes'], checklist=request.form.get('checklist',''), photo=filename)
        db.session.add(patrol)
        db.session.commit()
        return redirect(url_for('patrols.index'))
    return render_template('patrols/add.html')
