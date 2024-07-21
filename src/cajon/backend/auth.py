"""Auth."""

# external
from flask import Blueprint, flash, render_template, request

auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    """Login View."""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        _handle_signup(name, email, password1, password2)
    return render_template("auth/signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Login View."""
    return render_template("auth/login.html")


# accessories
def _handle_signup(name: str, email: str, password1: str, password2: str):
    # TODO: sanitize input
    if not name:
        flash("Name cannot be empty.", category="warning")
        return False
    if len(email) < 4:
        flash("Email is too short.", category="warning")
        return False
    if password1 != password2:
        flash("Passwords do not match.", category="warning")
        return False
    if len(password2) < 8:
        flash("Password is too short.", category="warning")
        return False
    flash("Account created.", category="success")
    return True
