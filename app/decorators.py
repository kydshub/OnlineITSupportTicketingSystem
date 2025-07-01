from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(roles):
    """
    Decorator to restrict access to users with specific roles.
    :param roles: A list or tuple of role names that are allowed.
    """
    if not isinstance(roles, (list, tuple)):
        roles = [roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                # This should ideally be handled by @login_required first,
                # but as a safeguard.
                abort(401) # Unauthorized
            if current_user.role not in roles:
                abort(403) # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specific decorators can be made from this:
def admin_required(f):
    return role_required(['admin'])(f)

def it_support_required(f):
    return role_required(['it_support', 'admin'])(f) # Admins can also do IT tasks
