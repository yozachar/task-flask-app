"""Models."""

# external
from flask_login import UserMixin

# local
from . import db


class User(db.Model, UserMixin):
    """User."""

    # TODO: front-end form validation
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    name = db.Column(db.String(120))

    def get_id(self):
        """Get user id."""
        return self.uid
