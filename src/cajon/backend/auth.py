"""Auth."""

# external
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

# local
from . import db
from ._utils import auth_required, authenticated, expect_db_error
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["GET", "POST"])
@authenticated
def signup():
    """Login View."""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if _signup_checklist(name, email, password1, password2):
            return _create_user(name, email, password1)
    return render_template("auth/signup.html")


@auth.route("/login", methods=["GET", "POST"])
@authenticated
def login():
    """Login View."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if _login_checklist(email, password) and (login_redirect := _login_user(email, password)):
            return login_redirect
    return render_template("auth/login.html")


@auth.route("/logout")
@auth_required
def logout():
    """Logout."""
    logout_user()
    return redirect(url_for("auth.login"))


# --------------> accessory functions <--------------


def _login_checklist(email: str, password: str):
    # TODO: sanitize input
    if len(email) < 4:
        flash("Email is too short.", category="warning")
        return False
    if len(password) < 8:
        flash("Password is too short.", category="warning")
        return False
    return True


def _login_user(email: str, password: str):
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Unable to find user. Please register an account.", category="error")
        return
    if check_password_hash(user.password, password):
        login_user(user, remember=True)
        flash("Login successful!", category="success")
        return redirect(url_for("views.home"))
    flash("Incorrect login credentials. Please try again.", category="error")
    return


def _signup_checklist(name: str, email: str, password1: str, password2: str):
    # TODO: sanitize input
    _ = name
    if len(email) < 4:
        flash("Email is too short.", category="warning")
        return False
    if password1 != password2:
        flash("Passwords do not match.", category="warning")
        return False
    if len(password2) < 8:
        flash("Password is too short.", category="warning")
        return False
    user = User.query.filter_by(email=email).first()
    if user:
        flash("User already exists. Please login.", category="error")
        return False
    return True


@expect_db_error
def _create_user(name: str, email: str, password: str):
    user = User(
        name=name,  # pyright: ignore[reportCallIssue]
        email=email,  # pyright: ignore[reportCallIssue]
        password=generate_password_hash(password, method="pbkdf2:sha256"),  # pyright: ignore[reportCallIssue]
    )
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    flash("Account was created!", category="success")
    return redirect(url_for("views.home"))
