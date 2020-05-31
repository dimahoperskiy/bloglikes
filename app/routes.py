import os
import secrets

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, \
    ResetPasswordForm
from app.models import User, Post, Like


def save_picture(form_picture):
    random_hex = secrets.token_hex(6)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, Like=Like, index_url=True)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url, Like=Like, explore_url=True)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_id = user.id
    image_file = url_for('static', filename='pics/' + user.ava)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', title='Profile', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, image_file=image_file, Like=Like, user_url=True)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if form.profile_pic.data:
            picture_file = save_picture(form.profile_pic.data)
            current_user.ava = picture_file
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


# login logout register


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.ava = 'default.jpg'
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# reset password


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# follow unfollow


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))


# likes dislikes delete post


@app.route('/user/<username>/delete/<post>')
@login_required
def delete(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post1 = Post.query.filter_by(id=post).first_or_404()
    likes = Like.query.filter_by(post_id=post).all()
    for like in likes:
        db.session.delete(like)
    post1.delete()
    flash(_('You have deleted your post'))
    return redirect(url_for('user', username=username))


@app.route('/user/<username>/like_user/<post>')
@login_required
def like_user(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post).first_or_404()
    l = Like(user_id=user.id, post_id=post.id, liked_id=current_user.id)
    db.session.add(l)
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/user/<username>/dislike_user/<post>')
@login_required
def dislike_user(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post).first_or_404()
    l = Like.query.filter_by(post_id=post.id).first_or_404()
    l.delete()
    return redirect(url_for('user', username=username))


@app.route('/user/<username>/like_index/<post>')
@login_required
def like_index(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post).first_or_404()
    l = Like(user_id=user.id, post_id=post.id, liked_id=current_user.id)
    db.session.add(l)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/user/<username>/dislike_index/<post>')
@login_required
def dislike_index(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post).first_or_404()
    l = Like.query.filter_by(post_id=post.id).first_or_404()
    l.delete()
    return redirect(url_for('index'))


@app.route('/user/<username>/like_explore/<post>')
@login_required
def like_explore(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post).first_or_404()
    l = Like(user_id=user.id, post_id=post.id, liked_id=current_user.id)
    db.session.add(l)
    db.session.commit()
    return redirect(url_for('explore'))


@app.route('/user/<username>/dislike_explore/<post>')
@login_required
def dislike_explore(username, post):
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post).first_or_404()
    l = Like.query.filter_by(post_id=post.id).first_or_404()
    l.delete()
    return redirect(url_for('explore'))



