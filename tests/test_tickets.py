from tests.base import BaseTestCase
from app.models import User, Ticket, Equipment
from app import db
from flask import url_for

class TestTicketRoutes(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create a standard user and an IT support user for testing roles
        self.employee_user = self.register_user(username="emp", email="emp@test.com", password="password", role="employee")
        self.it_user = self.register_user(username="itsupport", email="it@test.com", password="password", role="it_support")

        self.equipment1 = Equipment(name="Laptop01", type="Laptop", serial_number="SN001")
        db.session.add(self.equipment1)
        db.session.commit()

    def test_create_ticket_page_loads_for_authenticated_user(self):
        self.login_user(username="emp", password="password")
        response = self.client.get(url_for('tickets.create_ticket'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Ticket', response.data)

    def test_employee_creates_ticket_successfully(self):
        self.login_user(username="emp", password="password")
        response = self.client.post(
            url_for('tickets.create_ticket'),
            data=dict(
                title='My PC is broken',
                description='It does not turn on.',
                priority='High',
                equipment_id=self.equipment1.id
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200) # Redirects to view_ticket
        self.assertIn(b'Ticket created successfully!', response.data)
        self.assertIn(b'Ticket #1: My PC is broken', response.data) # Assuming this is the first ticket

        ticket = Ticket.query.filter_by(title='My PC is broken').first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.reporter_id, self.employee_user.id)
        self.assertEqual(ticket.priority, 'High')
        self.assertEqual(ticket.equipment_id, self.equipment1.id)
        self.assertEqual(ticket.status, 'Open') # Default status

    def test_list_tickets_for_employee(self):
        # Employee creates a ticket
        self.login_user(username="emp", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='Emp Ticket 1', description='Desc 1', priority='Low'), follow_redirects=True)

        # IT Support creates a ticket (should not be visible to employee on their list)
        self.login_user(username="itsupport", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='IT Ticket 1', description='Desc IT', priority='Medium'), follow_redirects=True)

        # Employee logs back in and views their tickets
        self.login_user(username="emp", password="password")
        response = self.client.get(url_for('tickets.list_tickets'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Reported Tickets', response.data)
        self.assertIn(b'Emp Ticket 1', response.data)
        self.assertNotIn(b'IT Ticket 1', response.data)

    def test_list_tickets_for_it_support(self):
        # Employee creates a ticket
        self.login_user(username="emp", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='Emp Ticket Alpha', description='Desc Alpha', priority='Low'), follow_redirects=True)

        # IT Support creates a ticket
        self.login_user(username="itsupport", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='IT Ticket Beta', description='Desc Beta', priority='Medium'), follow_redirects=True)

        # IT Support views tickets (should see all)
        response = self.client.get(url_for('tickets.list_tickets'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Tickets', response.data)
        self.assertIn(b'Emp Ticket Alpha', response.data)
        self.assertIn(b'IT Ticket Beta', response.data)

    def test_view_own_ticket_employee(self):
        self.login_user(username="emp", password="password")
        # Create a ticket as employee
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='Viewable Ticket', description='...', priority='Low'), follow_redirects=True)
        ticket = Ticket.query.filter_by(title='Viewable Ticket').first()

        response = self.client.get(url_for('tickets.view_ticket', ticket_id=ticket.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Viewable Ticket', response.data)

    def test_view_other_users_ticket_employee_permission_denied(self):
        # IT support creates a ticket
        self.login_user(username="itsupport", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='IT Only Ticket', description='...', priority='Low'), follow_redirects=True)
        it_ticket = Ticket.query.filter_by(title='IT Only Ticket').first()

        # Employee tries to view it
        self.login_user(username="emp", password="password")
        response = self.client.get(url_for('tickets.view_ticket', ticket_id=it_ticket.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to list_tickets
        self.assertIn(b'You do not have permission to view this ticket.', response.data)
        self.assertNotIn(b'IT Only Ticket', response.data) # Should not see the ticket content

    def test_it_support_can_view_any_ticket(self):
        # Employee creates a ticket
        self.login_user(username="emp", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='Employee Created Ticket For IT', description='...', priority='Low'), follow_redirects=True)
        emp_ticket = Ticket.query.filter_by(title='Employee Created Ticket For IT').first()

        # IT Support logs in and views it
        self.login_user(username="itsupport", password="password")
        response = self.client.get(url_for('tickets.view_ticket', ticket_id=emp_ticket.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Employee Created Ticket For IT', response.data)

    def test_it_support_updates_ticket(self):
        self.login_user(username="emp", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='To Be Updated', description='Original', priority='Low'), follow_redirects=True)
        ticket_to_update = Ticket.query.filter_by(title='To Be Updated').first()

        self.login_user(username="itsupport", password="password")
        response = self.client.post(
            url_for('tickets.update_ticket', ticket_id=ticket_to_update.id),
            data=dict(
                title='Updated Title',
                description='Updated Description',
                priority='Urgent',
                status='In Progress',
                assignee_id=self.it_user.id # Assign to self (IT user)
            ),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ticket updated successfully!', response.data)
        self.assertIn(b'Updated Title', response.data)
        self.assertIn(b'Status: In Progress', response.data)
        self.assertIn(b'Priority: Urgent', response.data)
        self.assertIn(b'Assigned to: itsupport', response.data)

        updated_ticket_db = Ticket.query.get(ticket_to_update.id)
        self.assertEqual(updated_ticket_db.title, 'Updated Title')
        self.assertEqual(updated_ticket_db.status, 'In Progress')
        self.assertEqual(updated_ticket_db.assignee_id, self.it_user.id)

    def test_add_comment_to_ticket(self):
        self.login_user(username="emp", password="password")
        self.client.post(url_for('tickets.create_ticket'), data=dict(title='Ticket For Commenting', description='...', priority='Low'), follow_redirects=True)
        ticket = Ticket.query.filter_by(title='Ticket For Commenting').first()

        # Employee adds a comment
        response = self.client.post(
            url_for('tickets.add_comment', ticket_id=ticket.id),
            data=dict(body='This is a comment from the employee.'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Comment added.', response.data)
        self.assertIn(b'This is a comment from the employee.', response.data)

        # IT Support adds a comment
        self.login_user(username="itsupport", password="password")
        response = self.client.post(
            url_for('tickets.add_comment', ticket_id=ticket.id),
            data=dict(body='IT support here, looking into it.'),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Comment added.', response.data)
        self.assertIn(b'IT support here, looking into it.', response.data)

        # Check both comments are there
        self.assertIn(b'This is a comment from the employee.', response.data)


if __name__ == '__main__':
    unittest.main()
