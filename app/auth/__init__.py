from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates')

# Import routes and forms after creating blueprint
from . import routes
# We will create forms.py later, but good to anticipate the import
# from . import forms
