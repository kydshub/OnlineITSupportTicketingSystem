from flask import Blueprint

bp = Blueprint('tickets', __name__, template_folder='templates')

# Import routes and forms after creating blueprint
from . import routes
# from . import forms
