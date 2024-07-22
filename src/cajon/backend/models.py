"""Models."""

# external
from flask_login import UserMixin

# local
from . import db


class User(db.Model, UserMixin):
    """User."""

    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(37), unique=True)
    password = db.Column(db.String(37))
    name = db.Column(db.String(148))
