'''
routes.py: Handles URL routing. Chooses which view function, template, or web form to show user depending on URL
'''
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime


# @ are decorators that tell Flask what URL trigger the below function
@app.before_request
def before_request():  # tracks when user was last seen, writes to db
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():  # shows form for adding a post and all followed posts
    form = PostForm()
    if form.validate_on_submit():  # if submit button is pressed
        post = Post(body=form.post.data, author=current_user)  # adding post
        db.session.add(post)
        db.session.commit()
        flash('Your post has been submitted!')
        return redirect(url_for('index'))
    page = request.args.get(key='page', default=1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)  # False parameter returns empty page instead of 404 error if trying to navigate to a page that doesn't exist
    if posts.has_next:
        next_url = url_for('index', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('index', page=posts.prev_num)
    else:
        prev_url = None
    return render_template('index.html', title='Home Page', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)  # items is list of items retrieved for selected page

@app.route('/login', methods=['GET', 'POST'])  # GET requests(server->client), POST requests(client->server)
def login():
    if current_user.is_authenticated:  # acounts for when logged in user finds herself on login page
        return redirect(url_for('index'))  # just redirects them to index
    form = LoginForm()
    if form.validate_on_submit():  # run below if they press submit (POST)
        user = User.query.filter_by(username=form.username.data).first()  ## use .first() when you only have one result (in our case a unique user)
        if user is None or user.check_password(form.password.data) == False:  # if username field is empty or password doesn't match
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)  # Flask_Login logs in user

        # now we want to decide where the user is redirected to after successful login
        next_page = request.args.get('next')  # gets value of 'next' parameter in string query
        if not next_page or url_parse(next_page).netloc != '':  # if login URL doesn't have next argument or if URL is relative(within the site of this application)
            next_page = url_for('index')
        return redirect(url_for('index'))  # do this action if next is set to a full URL with a domain name (goal is to not allow `next` parameter to leave site)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')  # logout page
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])  # registration page
def register():
    if current_user.is_authenticated:  # make sure user isn't already logged in
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():  # if they press submit button
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')  # profile page for User
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()  # returns 404 if no user by that username found
    page = request.args.get(key='page', default=1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)  # False parameter returns empty page instead of 404 error if trying to navigate to a page that doesn't exist
    if posts.has_next:
        next_url = url_for('user', username=user.username, page=posts.next_num)  # need username = user.username argument because url_for has to point back to same profile
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('user', username=user.username, page=posts.prev_num)
    else:
        prev_url = None
    form = EmptyForm()  # add options to follow or unfollow, specified by username.
    return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():  # run below if they press submit button
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':  # for when you are already logged in and want to edit your existing profile
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:  # redirect to index page if not logged in
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)  # helper function
        flash('Please check your email to reset your password.')  # flash even if email is not recognized so this can't be used to figure out if someone is registered or not
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
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


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):  # followbutton is rendered in User page
    form = EmptyForm()
    if form.validate_on_submit():  # run below once they press submit button
        user = User.query.filter_by(username=username).first()
        if user is None:  # if there is no user redirect to index
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:  # if user tries to follow him/herself
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You have unfollowed {} :-('.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get(key='page', default=1, type=int)  # request.args.get with key page is getting string query in case user presses link for page 2, 3, etc... otherwise default page 1
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)  # False parameter returns empty page instead of 404 error if trying to navigate to a page that doesn't exist
    if posts.has_next:
        next_url = url_for('explore', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('explore', page=posts.prev_num)
    else:
        prev_url = None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)  # page.items is list of items retrieved for selected page
