from app import create_app, db # db can be imported for scripting if needed, like creating initial data.
from app.models import User, Ticket, Equipment # Import models to ensure they are known for db operations if any are done here.

app = create_app()

if __name__ == '__main__':
    # Note: For production, use a WSGI server like Gunicorn or Waitress
    # For development, Flask's built-in server is fine.
    # The 'flask run' command will automatically detect create_app or app in run.py or app.py
    # Setting FLASK_APP=run.py (or FLASK_APP=app if using app/__init__.py directly)
    # allows 'flask run', 'flask db' etc. to work.

    # To make `flask run` work without setting FLASK_APP explicitly for this structure:
    # 1. Ensure `app` instance is created at global scope in this file.
    # 2. Or, ensure `create_app` is available.
    # The `app = create_app()` line above handles this.

    # Example: You could add a CLI command to create a default admin user here
    # with app.app_context():
    #     if not User.query.filter_by(username='admin').first():
    #         admin_user = User(username='admin', email='admin@example.com', role='admin')
    #         admin_user.set_password('adminpassword')
    #         db.session.add(admin_user)
    #         db.session.commit()
    #         print("Admin user created.")

    app.run(debug=True) # debug=True is fine for development
