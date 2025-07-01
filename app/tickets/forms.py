from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models import User, Equipment # To populate assignee and equipment choices

# Choices for ticket status and priority
STATUS_CHOICES = [('Open', 'Open'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved'), ('Closed', 'Closed')]
PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Urgent', 'Urgent')]

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=PRIORITY_CHOICES, default='Medium', validators=[DataRequired()])
    equipment_id = SelectField('Associated Equipment (Optional)', coerce=int, validators=[Optional()])
    submit = SubmitField('Create Ticket')

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        # Populate equipment choices. (0, 'None') allows not selecting any.
        # Show only 'In Stock' or equipment already assigned to the current user (if applicable)
        # For simplicity now, show all non-retired. Can be refined.
        self.equipment_id.choices = [(0, '--- None ---')] + \
                                    [(e.id, f"{e.name} (S/N: {e.serial_number or 'N/A'})")
                                     for e in Equipment.query.filter(Equipment.status != 'Retired')
                                     .order_by(Equipment.name).all()]

class UpdateTicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=PRIORITY_CHOICES, validators=[DataRequired()])
    status = SelectField('Status', choices=STATUS_CHOICES, validators=[DataRequired()])
    assignee_id = SelectField('Assign To', coerce=int, validators=[Optional()])
    equipment_id = SelectField('Associated Equipment (Optional)', coerce=int, validators=[Optional()])
    submit = SubmitField('Update Ticket')

    def __init__(self, *args, **kwargs):
        super(UpdateTicketForm, self).__init__(*args, **kwargs)
        # Populate assignee choices
        self.assignee_id.choices = [(0, '--- Unassign ---')] + \
                                   [(user.id, user.username) for user in User.query
                                    .filter(User.role.in_(['it_support', 'admin']))
                                    .order_by(User.username).all()]
        # Populate equipment choices
        self.equipment_id.choices = [(0, '--- None ---')] + \
                                    [(e.id, f"{e.name} (S/N: {e.serial_number or 'N/A'})")
                                     for e in Equipment.query.filter(Equipment.status != 'Retired')
                                     .order_by(Equipment.name).all()]

        # Set default for assignee_id if it's not provided (e.g. when form is created for an unassigned ticket)
        # The `obj=ticket` in routes.py usually handles populating fields from the model object.
        # However, if `ticket.assignee_id` is None, we want the dropdown to show '--- Unassign ---' (value 0).
        # WTForms SelectField with coerce=int will try to make None into int(None) which fails.
        # So, if self.assignee_id.data is None from the object, we can set it to 0.
        if self.assignee_id.data is None:
            self.assignee_id.data = 0
        if self.equipment_id.data is None:
            self.equipment_id.data = 0


class CommentForm(FlaskForm):
    body = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=1024)])
    submit = SubmitField('Add Comment')
