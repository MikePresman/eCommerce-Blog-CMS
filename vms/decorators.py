from functools import wraps
from flask import redirect, url_for, flash
from vms.models import User


def login_necessary(current_user):
    def wrap(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if current_user.is_authenticated is False:
                flash("You must be logged in to use this page")
                return redirect(url_for("login"))
            else:
                return func(*args, **kwargs)
        return decorator
    return wrap


def admin_only(current_user):
    def wrap(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                user = User.query.filter_by(id=current_user.id).first()
            except AttributeError as e:
                flash("Please login to view this page")
                return redirect(url_for("index"))
            if user.authority < 1:
                return redirect(url_for("index"))
            else:
                return func(*args, **kwargs)
        return decorator
    return wrap
