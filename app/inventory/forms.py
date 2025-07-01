from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional
from app.models import User # To populate user choices for assignment

EQUIPMENT_STATUS_CHOICES = [
    ('In Stock', 'In Stock'),
    ('Assigned', 'Assigned'),
    ('In Repair', 'In Repair'),
    ('Retired', 'Retired')
]

EQUIPMENT_TYPE_CHOICES = [
    ('Laptop', 'Laptop'),
    ('Desktop', 'Desktop'),
    ('Monitor', 'Monitor'),
    ('Keyboard', 'Keyboard'),
    ('Mouse', 'Mouse'),
    ('Printer', 'Printer'),
    ('Router', 'Router'),
    ('Switch', 'Switch'),
    ('Server', 'Server'),
    ('Other', 'Other')
]

class EquipmentForm(FlaskForm):
    name = StringField('Equipment Name/Identifier', validators=[DataRequired(), Length(max=120)])
    type = SelectField('Type', choices=EQUIPMENT_TYPE_CHOICES, validators=[DataRequired()])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    model_number = StringField('Model Number', validators=[Optional(), Length(max=100)])
    serial_number = StringField('Serial Number', validators=[Optional(), Length(max=100)]) # Should ideally be unique if not optional

    purchase_date = DateField('Purchase Date', validators=[Optional()])
    warranty_expiry_date = DateField('Warranty Expiry Date', validators=[Optional()])

    status = SelectField('Status', choices=EQUIPMENT_STATUS_CHOICES, default='In Stock', validators=[DataRequired()])
    # assigned_to_user_id will be handled in a separate form or part of the edit view logic
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Equipment')

class AssignEquipmentForm(FlaskForm):
    assigned_to_user_id = SelectField('Assign to User', coerce=int, validators=[Optional()]) # Optional to allow unassignment
    submit = SubmitField('Update Assignment')

    def __init__(self, *args, **kwargs):
        super(AssignEquipmentForm, self).__init__(*args, **kwargs)
        # Populate choices with all users. (0, 'Unassign') allows clearing the assignment.
        self.assigned_to_user_id.choices = [(0, 'Unassign / In Stock')] + [(user.id, f"{user.username} ({user.email})") for user in User.query.order_by(User.username).all()]

# We might not need a separate EditEquipmentForm if EquipmentForm is flexible enough
# and existing data is populated correctly. For now, EquipmentForm can serve both.
