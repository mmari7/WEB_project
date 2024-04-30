from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Your email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Password again', validators=[DataRequired()])
    name = StringField('Username', validators=[DataRequired()])
    about = TextAreaField("About you")
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Your email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')

