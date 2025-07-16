import csv
import os
from flask import Blueprint, current_app, send_file, request, render_template
from ..models import Patrol, Hazard, Maintenance, TrailCam
from .. import db
from fpdf import FPDF

bp = Blueprint('reports', __name__)

@bp.route('/')
def index():
    return render_template('reports/index.html')


def export_csv(model, filename, headers, rows):
    path = os.path.join(current_app.instance_path, filename)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return path

@bp.route('/<name>.csv')
def csv_export(name):
    if name == 'patrols':
        rows = [(p.date, p.area, p.notes) for p in Patrol.query.all()]
        path = export_csv(Patrol, 'patrols.csv', ['date','area','notes'], rows)
    elif name == 'hazards':
        rows = [(h.date_reported, h.location, h.severity, h.status) for h in Hazard.query.all()]
        path = export_csv(Hazard, 'hazards.csv', ['date','location','severity','status'], rows)
    elif name == 'maintenance':
        rows = [(m.date_reported, m.equipment, m.issue, m.done) for m in Maintenance.query.all()]
        path = export_csv(Maintenance, 'maintenance.csv', ['date','equipment','issue','done'], rows)
    elif name == 'trailcams':
        rows = [(t.date, t.location, t.filename) for t in TrailCam.query.all()]
        path = export_csv(TrailCam, 'trailcams.csv', ['date','location','filename'], rows)
    else:
        return 'unknown', 404
    return send_file(path, as_attachment=True)

class PDF(FPDF):
    pass

@bp.route('/<name>.pdf')
def pdf_export(name):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)

    if name == 'patrols':
        pdf.cell(0,10,'Patrols', ln=1)
        for p in Patrol.query.all():
            pdf.cell(0,10,f"{p.date} {p.area} {p.notes}", ln=1)
    elif name == 'hazards':
        pdf.cell(0,10,'Hazards', ln=1)
        for h in Hazard.query.all():
            pdf.cell(0,10,f"{h.date_reported} {h.location} {h.severity} {h.status}", ln=1)
    elif name == 'maintenance':
        pdf.cell(0,10,'Maintenance', ln=1)
        for m in Maintenance.query.all():
            pdf.cell(0,10,f"{m.date_reported} {m.equipment} {m.issue}", ln=1)
    elif name == 'trailcams':
        pdf.cell(0,10,'Trail Cams', ln=1)
        for t in TrailCam.query.all():
            pdf.cell(0,10,f"{t.date} {t.location} {t.filename}", ln=1)
    else:
        return 'unknown', 404

    path = os.path.join(current_app.instance_path, f'{name}.pdf')
    pdf.output(path)
    return send_file(path, as_attachment=True)
