import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from .. import db
from ..models import Hazard

bp = Blueprint('hazards', __name__)

@bp.route('/')
def index():
    hazards = Hazard.query.order_by(Hazard.date_reported.desc()).all()
    return render_template('hazards/index.html', hazards=hazards)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        photo = request.files.get('photo')
        filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'hazards', filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            photo.save(path)
        hazard = Hazard(location=request.form['location'], description=request.form['description'], severity=request.form['severity'], status=request.form['status'], photo=filename)
        db.session.add(hazard)
        db.session.commit()
        return redirect(url_for('hazards.index'))
    return render_template('hazards/add.html')
