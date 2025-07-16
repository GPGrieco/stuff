import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# SQLAlchemy database

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'mineops.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, 'uploads')
    )

    if test_config:
        app.config.update(test_config)

    # ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa

    # register blueprints
    from .routes.patrols import bp as patrols_bp
    from .routes.hazards import bp as hazards_bp
    from .routes.maintenance import bp as maintenance_bp
    from .routes.trailcams import bp as trailcams_bp
    from .routes.reports import bp as reports_bp

    app.register_blueprint(patrols_bp, url_prefix='/patrols')
    app.register_blueprint(hazards_bp, url_prefix='/hazards')
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')
    app.register_blueprint(trailcams_bp, url_prefix='/trailcams')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    from flask import send_from_directory

    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app
