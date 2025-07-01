from tests.base import BaseTestCase
from app.models import User
from app import db
from flask import url_for

class TestAuthRoutes(BaseTestCase):

    def test_registration_page_loads(self):
        response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_page_loads(self):
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_user_registration(self):
        response = self.client.post(
            url_for('auth.register'),
            data=dict(
                username='newuser',
                email='newuser@example.com',
                password='password123',
                confirm_password='password123'
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Should redirect to login
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')

    def test_duplicate_username_registration(self):
        self.register_user(username='existinguser', email='exists@example.com', password='password')
        response = self.client.post(
            url_for('auth.register'),
            data=dict(
                username='existinguser', # Duplicate username
                email='newemail@example.com',
                password='password123',
                confirm_password='password123'
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Stays on registration page (or re-renders it)
        self.assertIn(b'That username is already taken.', response.data)

    def test_duplicate_email_registration(self):
        self.register_user(username='anotheruser', email='existing@example.com', password='password')
        response = self.client.post(
            url_for('auth.register'),
            data=dict(
                username='newusername',
                email='existing@example.com', # Duplicate email
                password='password123',
                confirm_password='password123'
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'That email is already in use.', response.data)

    def test_user_login_successful(self):
        self.register_user(username='loginuser', email='login@example.com', password='password123')
        response = self.client.post(
            url_for('auth.login'),
            data=dict(username='loginuser', password='password123'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to index
        self.assertIn(b'Welcome back, loginuser!', response.data) # Flash message
        self.assertIn(b'Logout (loginuser)', response.data) # Nav bar shows logout

    def test_user_login_invalid_username(self):
        self.register_user(username='realuser', email='real@example.com', password='password123')
        response = self.client.post(
            url_for('auth.login'),
            data=dict(username='fakeuser', password='password123'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Stays on login
        self.assertIn(b'Invalid username or password', response.data)
        self.assertNotIn(b'Logout', response.data)

    def test_user_login_invalid_password(self):
        self.register_user(username='loginuser2', email='login2@example.com', password='correctpassword')
        response = self.client.post(
            url_for('auth.login'),
            data=dict(username='loginuser2', password='wrongpassword'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Stays on login
        self.assertIn(b'Invalid username or password', response.data)
        self.assertNotIn(b'Logout', response.data)

    def test_user_logout(self):
        self.register_user(username='logoutuser', email='logout@example.com', password='password')
        self.login_user(username='logoutuser', password='password') # Log in first

        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to index
        self.assertIn(b'You have been logged out.', response.data)
        self.assertIn(b'Login', response.data) # Nav bar shows login again
        self.assertNotIn(b'Logout (logoutuser)', response.data)

    def test_access_protected_route_unauthenticated(self):
        response = self.client.get(url_for('tickets.list_tickets'), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to login
        self.assertIn(b'Please log in to access this page.', response.data) # Flash message
        self.assertIn(b'Login', response.data) # On login page

if __name__ == '__main__':
    unittest.main()
