from app import create_app, db
from app.models import Patrol, Hazard, Maintenance, TrailCam

app = create_app()
with app.app_context():
    db.create_all()
    if not Patrol.query.first():
        p = Patrol(area='Main Gate', notes='All clear', checklist='Gate Locked')
        h = Hazard(location='North Pit', description='Loose rocks', severity='Medium', status='Logged')
        m = Maintenance(equipment='Generator', issue='Oil change', done=True, notes='Changed oil')
        t = TrailCam(location='Water Hole', filename='', notes='First setup')
        db.session.add_all([p,h,m,t])
        db.session.commit()
        print('Sample data inserted.')
    else:
        print('Data already exists.')
