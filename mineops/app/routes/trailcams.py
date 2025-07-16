import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from .. import db
from ..models import TrailCam

bp = Blueprint('trailcams', __name__)

@bp.route('/')
def index():
    cams = TrailCam.query.order_by(TrailCam.date.desc()).all()
    return render_template('trailcams/index.html', cams=cams)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        files = request.files.getlist('photos')
        for f in files:
            if not f or not f.filename:
                continue
            filename = secure_filename(f.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'trailcams', filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            f.save(path)
            cam = TrailCam(location=request.form['location'], filename=filename, notes=request.form.get('notes',''))
            db.session.add(cam)
        db.session.commit()
        return redirect(url_for('trailcams.index'))
    return render_template('trailcams/add.html')
