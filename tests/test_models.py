from tests.base import BaseTestCase
from app.models import User, Ticket, Equipment, Comment
from app import db
from datetime import datetime

class TestModelCreation(BaseTestCase):

    def test_user_creation(self):
        u = User(username='john', email='john@example.com', role='employee')
        u.set_password('cat')
        db.session.add(u)
        db.session.commit()

        user_from_db = User.query.filter_by(username='john').first()
        self.assertIsNotNone(user_from_db)
        self.assertEqual(user_from_db.email, 'john@example.com')
        self.assertTrue(user_from_db.check_password('cat'))
        self.assertFalse(user_from_db.check_password('dog'))
        self.assertEqual(user_from_db.role, 'employee')

    def test_equipment_creation(self):
        e = Equipment(name='Laptop XYZ', type='Laptop', serial_number='XYZ123', status='In Stock')
        db.session.add(e)
        db.session.commit()

        equipment_from_db = Equipment.query.filter_by(serial_number='XYZ123').first()
        self.assertIsNotNone(equipment_from_db)
        self.assertEqual(equipment_from_db.name, 'Laptop XYZ')
        self.assertEqual(equipment_from_db.status, 'In Stock')

    def test_ticket_creation(self):
        user = self.register_user(username="reporter", email="reporter@test.com", password="password")
        equip = Equipment(name='Test PC', type='Desktop', serial_number='TPC001')
        db.session.add(equip)
        db.session.commit()

        t = Ticket(title='PC Broken', description='Screen is blank', priority='High',
                   reporter_id=user.id, equipment_id=equip.id)
        db.session.add(t)
        db.session.commit()

        ticket_from_db = Ticket.query.filter_by(title='PC Broken').first()
        self.assertIsNotNone(ticket_from_db)
        self.assertEqual(ticket_from_db.reporter.username, 'reporter')
        self.assertEqual(ticket_from_db.priority, 'High')
        self.assertIsNotNone(ticket_from_db.created_at)
        self.assertEqual(ticket_from_db.associated_equipment.name, 'Test PC')

    def test_comment_creation(self):
        user = self.register_user(username="commenter", email="commenter@test.com", password="password")
        ticket = self.create_test_ticket(user_id=user.id, title="Ticket for comment")

        c = Comment(body='This is a test comment.', user_id=user.id, ticket_id=ticket.id)
        db.session.add(c)
        db.session.commit()

        comment_from_db = Comment.query.filter_by(body='This is a test comment.').first()
        self.assertIsNotNone(comment_from_db)
        self.assertEqual(comment_from_db.author.username, 'commenter')
        self.assertEqual(comment_from_db.ticket.title, 'Ticket for comment')
        self.assertIsNotNone(comment_from_db.created_at)

    def test_user_roles(self):
        admin_user = User(username='admin_user', email='admin@example.com', role='admin')
        it_user = User(username='it_user', email='it@example.com', role='it_support')
        emp_user = User(username='emp_user', email='emp@example.com', role='employee')
        db.session.add_all([admin_user, it_user, emp_user])
        db.session.commit()

        self.assertEqual(User.query.filter_by(role='admin').count(), 1)
        self.assertEqual(User.query.filter_by(role='it_support').count(), 1)
        self.assertEqual(User.query.filter_by(role='employee').count(), 1)

    def test_ticket_timestamps(self):
        user1 = self.register_user()
        ticket = Ticket(title="Timestamp Test", description="Testing auto timestamps", reporter_id=user1.id)
        db.session.add(ticket)
        db.session.commit()

        self.assertIsNotNone(ticket.created_at)
        self.assertIsNotNone(ticket.updated_at)
        initial_updated_at = ticket.updated_at

        # Simulate an update
        ticket.description = "Updated description"
        db.session.commit() # This should trigger onupdate for updated_at

        # Fetch again to ensure state is current
        db.session.refresh(ticket)
        self.assertGreater(ticket.updated_at, initial_updated_at)

if __name__ == '__main__':
    unittest.main()
