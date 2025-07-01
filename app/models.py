from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager # Import from app package (app/__init__.py)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='employee') # 'employee', 'it_support', 'admin'

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    reported_tickets = db.relationship('Ticket', foreign_keys='Ticket.reporter_id', backref='reporter', lazy=True)
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assignee_id', backref='assignee', lazy=True)
    equipment_assigned = db.relationship('Equipment', backref='assigned_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open') # e.g., 'Open', 'In Progress', 'Resolved', 'Closed'
    priority = db.Column(db.String(20), nullable=False, default='Medium') # e.g., 'Low', 'Medium', 'High', 'Urgent'

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)

    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)

    # Comments could be a separate model or a JSON field if the DB supports it well
    # For now, let's plan for a separate Comment model later if needed.

    def __repr__(self):
        return f'<Ticket {self.id} - {self.title}>'

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=False) # e.g., 'Laptop', 'Desktop', 'Monitor', 'Keyboard', 'Mouse'
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    model_number = db.Column(db.String(100), nullable=True)

    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiry_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(50), nullable=False, default='In Stock') # e.g., 'In Stock', 'Assigned', 'In Repair', 'Retired'
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship back to tickets (one piece of equipment can be associated with multiple tickets over time)
    tickets = db.relationship('Ticket', backref='associated_equipment', lazy=True)

    def __repr__(self):
        return f'<Equipment {self.name} ({self.serial_number})>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)

    author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    ticket = db.relationship('Ticket', backref=db.backref('comments', lazy='dynamic', order_by="Comment.created_at.asc()"))

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id} on Ticket {self.ticket_id}>'


# Optional: Association table for Many-to-Many between Tickets and Equipment if needed later
# class TicketEquipment(db.Model):
#     ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), primary_key=True)
#     equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
#     notes = db.Column(db.String(255), nullable=True) # e.g. "Component failed"
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

#     ticket = db.relationship("Ticket", backref=db.backref("ticket_equipment_associations", cascade="all, delete-orphan"))
#     equipment = db.relationship("Equipment", backref=db.backref("equipment_ticket_associations", cascade="all, delete-orphan"))

#     def __repr__(self):
#         return f'<TicketEquipment ticket_id={self.ticket_id} equipment_id={self.equipment_id}>'
