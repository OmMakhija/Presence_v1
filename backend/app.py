from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate

from backend.config import Config
from backend.models import db, User

migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.student import student_bp
    from backend.routes.teacher import teacher_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app


# 🔥 REQUIRED FOR GUNICORN
app = create_app()
