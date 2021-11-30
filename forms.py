from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, EqualTo

class Signup(FlaskForm):
    """Signup Form"""
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password',
        validators = [DataRequired(), EqualTo("password", message='Passwords need to match')])
    email = StringField('Email', validators=[DataRequired()])
    phone =  IntegerField('Phone', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class Login(FlaskForm):
    """Login Form"""
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Log In')

class Alert(FlaskForm):
    """Create an Alert Form"""
    daterange = StringField('Date Range', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Log In')