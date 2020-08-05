# auth/routes.py: Handles AUTHENTIFICATION RELATED routing
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.auth.emails import send_password_reset_email
from app.models import User
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])  # GET requests(server->client), POST requests(client->server)
def login():
    if current_user.is_authenticated:  # acounts for when logged in user finds herself on login page
        return redirect(url_for('main.index'))  # just redirects them to index
    form = LoginForm()
    if form.validate_on_submit():  # run below if they press submit (POST)
        user = User.query.filter_by(username=form.username.data).first()  # use .first() because only want one result
        if user is None or user.check_password(form.password.data) == False:  # if username field is empty or password doesn't match
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)  # Flask_Login logs in user

        # decide where the user is redirected to after successful login
        next_page = request.args.get('next')  # to continue to user's intended destination after login
        if not next_page or url_parse(next_page).netloc != '':  # if login URL doesn't have next argument or if URL isn't relative(goal is to not allow `next` parameter to leave site)
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')  # logout page
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])  # registration page
def register():
    if current_user.is_authenticated:  # make sure user isn't already logged in
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():  # if they press submit button
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:  # redirect to index page if not logged in
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Please check your email to reset your password.')  # flash even if email is not recognized so this can't be used to figure out if someone is registered or not
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:  # if user isn't logged in
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:  # if user == None / User.verify_reset_password_token receives invalid or expired token
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():  # if submit button was pressed
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
