import unittest
import os
from app import create_app, db
from app.models import User, Ticket, Equipment, Comment # Import all models

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        # Use a separate config or override existing ones for tests
        os.environ['FLASK_ENV'] = 'testing' # Good practice
        # In-memory SQLite for tests
        # Note: For app factory, we might need to pass config overrides directly.
        # Or, ensure create_app() checks for FLASK_ENV or a specific test config.

        # Let's adjust create_app to accept a test_config
        # For now, I'll assume create_app uses a different DB URI if FLASK_ENV is testing
        # or use a dedicated test config.

        # A better way: modify create_app to accept test_config
        # For now, let's assume app.config['SQLALCHEMY_DATABASE_URI'] can be overridden
        # AFTER app creation but BEFORE db.create_all() if db is not created in create_app.
        # However, our current create_app in app/__init__.py uses instance folder.
        # We need a way to make sure tests use a separate, temporary database.

        # Simplest approach for now: modify create_app to accept a config object or name
        # Or, modify the config directly if using FLASK_ENV=testing is picked up by create_app()

        # For now, I'll create a new app instance with test config here
        self.app = create_app() # This will use the default instance/site.db or what's in .env

        # Override the database URI for testing AFTER app creation, if create_app doesn't handle test config
        # This is a bit of a hack. Ideally, create_app would take a config_name='testing'
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite for tests
            "WTF_CSRF_ENABLED": False, # Disable CSRF for simpler form testing
            "LOGIN_DISABLED": False, # Ensure login is not disabled unless specifically for a test
            "SERVER_NAME": "localhost.localdomain" # For url_for to work without active server context
        })

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all() # Create tables in the in-memory database
        self.client = self.app.test_client() # Test client for making requests

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, username="testuser", email="test@example.com", password="password", role="employee"):
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def login_user(self, username="testuser", password="password"):
        return self.client.post(
            '/auth/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def create_test_ticket(self, user_id, title="Test Ticket", description="Test Desc", priority="Medium"):
        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            reporter_id=user_id
        )
        db.session.add(ticket)
        db.session.commit()
        return ticket

if __name__ == '__main__':
    unittest.main()
