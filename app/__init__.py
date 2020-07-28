'''
__init__.py: Hosts the app, initializes a Flask instance, intializes database instance
'''
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

app = Flask(__name__)  # initialize Flask instance
app.config.from_object(Config)  # fill config parameters from `Config.py` module
db = SQLAlchemy(app)  # intialize SQLAlchemy database instance
migrate = Migrate(app, db)  # initialize migration engine
login = LoginManager(app)
login.login_view = 'login'  # 'login' is name function for the login view

if not app.debug:  # only send logs when debug mode is off
    if app.config['MAIL_SERVER']:  # email logs if MAIL_SERVER is set up
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr = 'no-reply@' + app.config['MAIL_SERVER'],
            toaddrs = app.config['ADMINS'], subject = 'Microblog Failure',
            credentials = auth, secure = secure)
        mail_handler.setLevel(logging.ERROR)  # only reports errors not warnings
        app.logger.addHandler(mail_handler)  # attach SMTPHandler instance to app.logger object from Flask

    # implementing logging to files
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)  # max size of 10kB and backup last 10 logs
    file_handler.setFormatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')  # set format of logs
    file_handler.setLevel(logging.INFO)  # logs INFO level and below
    app.logger.addHandler(file_handler)  # attatch RotatingFileHandler instance to app.logger object from Flask

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import routes, models, errors  # imported on bottom to avoid circular imports
