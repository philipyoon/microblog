from threading import Thread
from flask_mail import Message
from flask import current_app
from app import mail

def send_async_email(app, msg):  # runs in a background thread invoked via Thread()
    with app.app_context():  # sends application context into custom thread because mail.send() needs the apps configuration files to access email server, app instance available via `current_app` variable from Flask
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):  # basic implementation of sending an email
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
