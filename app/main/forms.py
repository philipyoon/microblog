# from flask import request
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):  # saves original username
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):  # checks to see if username is taken
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):  # form for triggering follow and unfollow actions as a POST request with a CSRF token
    submit = SubmitField('Submit')  # submit button labeled Submit

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
            # 'formdata' points to where Flask-WTF gets form submissions; for GET
            # request point Flask-WTF at request.args, which is where Flask
            # writes query string arguments
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False  # disables CSRF protection default for clickable search links to work
        super(SearchForm, self).__init__(*args, **kwargs)
