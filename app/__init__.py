import os
import logging
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from logging.handlers import SMTPHandler, RotatingFileHandler
from elasticsearch import Elasticsearch

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'  # set view function to auth.login function
login.login_message = 'Please log in to access this page.'  # set custom default message
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()

def create_app(config_class=Config):  # creates flask application instance
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None  # create elasticsearch instance in global scope, sets it to None if URL isn't defined

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)  # connects all error handlers, view functions to application

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')  # url_prefix allows all routes handled under this blueprint to start with /auth

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:  # only send logs when debug and testing mode is off
        if app.config['LOG_TO_STDOUT']:  # logs to stdout if setup in config
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            # logging to files
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app
        
from app import models  # imported on bottom to avoid circular imports
