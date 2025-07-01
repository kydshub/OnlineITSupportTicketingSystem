import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True) # instance_relative_config=True allows for instance folder config

    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_secret_key'), # Default for dev, override in production
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) # Models need to be imported before migrate commands are run

    # Login manager configuration
    login_manager.login_view = 'auth.login' # Blueprint 'auth', route 'login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = "Please log in to access this page."


    # Import models here or ensure they are imported by blueprints
    # This ensures Flask-Migrate can see them
    from . import models

    # Import and register blueprints
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .tickets import bp as tickets_bp
    app.register_blueprint(tickets_bp, url_prefix='/tickets')

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    @app.route('/health')
    def health_check():
        return "OK", 200

    return app
