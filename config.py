import os
basedir = os.path.abspath(os.path.dirname(__file__))  # absolute path of directory where this config.py module resides

class Config(object):
    # good practice to set configuration from environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'password123' # SECRET_KEY config variable used to generate signatures or tokens, protection against CSRF attacks
    POSTS_PER_PAGE = 3

    # set to DATABASE_URL environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')  # backup that configures a databas named 'app.db' in parent directory (basedir)
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # disables tracking changes

    # set-up emailing errors
    MAIL_SERVER = os.environ.get('MAIL_SERVER')  # set server
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)  # set port
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None  # use encrypted connections
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['yoonphilip99@gmail.com']
