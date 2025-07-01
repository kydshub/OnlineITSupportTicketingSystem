from flask import render_template, Blueprint
from . import bp # Use the local blueprint instance
from flask_login import current_user # To tailor content

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html', title="Homepage")

# Example of how models might be used in a route later
# from app.models import User
# @bp.route('/users')
# def users():
#     all_users = User.query.all()
#     return render_template('main/users.html', users=all_users)
