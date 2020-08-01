'''
models.py: define User and Post models, implements follower relationship
'''
from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  # includes generic implementations for user model classes
from time import time
from hashlib import md5
import jwt

# creating association table to integrate follower relationship
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):  # User class inherits from db.Model, base class for all models from SQLAlchemy. Also inherits UserMixin to implement login
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # sets relationship between users and posts, allows for queries like user.posts
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(  # sets up querying what following relationships
        'User', secondary=followers,  # secondary is association table
        primaryjoin=(followers.c.follower_id == id),  # primaryjoin links follower user and association table
        secondaryjoin=(followers.c.followed_id == id),  # secondaryjoin links followed user and association table
        backref = db.backref('followers', lazy='dynamic'), lazy='dynamic')  # backref defines how followed entity will access their followers
            # dynamic sets up left and right queries to not run until specifically requested

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0  # use filter() vs filter_by() to set arbitrary filtering conditions

    def followed_posts(self):  # returns list of self's posts and followed user's posts
        others = Post.query.join(followers, (followers.c.followed_id == Post.user_id)  # join Posts table with follower association table where follower's followed_id == Post's user_id
            ).filter(followers.c.follower_id == self.id)  # filter out posts from users self isn't following
        own = Post.query.filter_by(user_id=self.id) # get own posts
        return others.union(own).order_by(Post.timestamp.desc())  # sort posts by time in descending order

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):  # reset token expires in 10 minutes
        return jwt.encode({'reset_password': self.id, 'exp':time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')  # decode's the byte sequence token as a string for conveniency

    @staticmethod  # can be invoked directly from class
    def verify_reset_password_token(token):
        try:  # if token is valid, value of reset_password key from token is ID of user, so can load the user and return it
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:  # if token is invalid or is expired
            return None
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # for ForeignKey parameter, 'user.id' refers to the id from User table

    def __repr__(self):
        return '<Post: {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))  # loads user from ID, ties in LoginManager and User from database
