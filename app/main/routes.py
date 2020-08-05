# main/routes.py: Handles general routing
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post
from app.main import bp


# @ are decorators that modify function, telling app what to do for diff URLs
@bp.before_request
def before_request():  # tracks when user was last seen, writes to db
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()  # explain

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():  # shows form for adding a post and all followed posts
    form = PostForm()
    if form.validate_on_submit():  # if submit button is pressed
        post = Post(body=form.post.data, author=current_user)  # adding post
        db.session.add(post)
        db.session.commit()
        flash('Your post has been submitted!')
        return redirect(url_for('main.index'))
    page = request.args.get(key='page', default=1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)  # False parameter returns empty page instead of 404 error if trying to navigate to a page that doesn't exist
    if posts.has_next:
        next_url = url_for('main.index', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('main.index', page=posts.prev_num)
    else:
        prev_url = None
    return render_template('index.html', title='Home', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)  # items is list of items retrieved for selected page

@bp.route('/user/<username>')  # profile page for User
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()  # returns 404 if no user by that username found
    page = request.args.get(key='page', default=1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)  # False parameter returns empty page instead of 404 error if trying to navigate to a page that doesn't exist
    if posts.has_next:
        next_url = url_for('main.user', username=user.username, page=posts.next_num)  # need username = user.username argument because url_for has to point back to same profile
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('main.user', username=user.username, page=posts.prev_num)
    else:
        prev_url = None
    form = EmptyForm()  # add options to follow or unfollow, specified by username.
    return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():  # run below if they press submit button
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':  # for when you are already logged in and want to edit your existing profile
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):  # followbutton is rendered in User page
    form = EmptyForm()
    if form.validate_on_submit():  # run below once they press submit button
        user = User.query.filter_by(username=username).first()
        if user is None:  # if there is no user redirect to index
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:  # if user tries to follow him/herself
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username))
        current_user.follow(user)
        db.session.commit()
        flash('You are now following {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You have unfollowed {} :-('.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get(key='page', default=1, type=int)  # request.args.get with key page is getting string query in case user presses link for page 2, 3, etc... otherwise default page 1
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)  # False parameter returns empty page instead of 404 error if trying to navigate to a page that doesn't exist
    if posts.has_next:
        next_url = url_for('main.explore', page=posts.next_num)
    else:
        next_url = None
    if posts.has_prev:
        prev_url = url_for('main.explore', page=posts.prev_num)
    else:
        prev_url = None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)  # page.items is list of items retrieved for selected page


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)
