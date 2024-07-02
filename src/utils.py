from functools import wraps
from flask import session, redirect, url_for

def check_logged_in(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function
