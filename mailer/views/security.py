from flask import request, flash, Blueprint, url_for, redirect, render_template
from flask_login import login_user,current_user,login_required,logout_user

from mailer.models.ab_users import Users

users_view = Blueprint('users_view', __name__)



@users_view.route("/signup", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('base.base_view'))
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        emailAlreadyRegistered = Users.query.filter_by(email=email).first()

        if emailAlreadyRegistered is not None:
            flash('Email already registered.')
        else:
            newuser = Users(firstname, lastname, email, password)
            newuser.add_to_db()
            return redirect(url_for('users_view.login'))

    return render_template("register.html", title="Sign up")


@users_view.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base.base_view'))
    if request.method == 'POST':
        email = request.values.get('email')
        password = request.values.get('password')
        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('base.base_view'))
        else:
            flash('Invalid email or password.')
    return render_template("login.html", title="Login")


@users_view.route('/logout')
@login_required
def logout():

    logout_user()
    flash('You have successfully been logged out.')
    return redirect(url_for('users_view.login'))
