from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired


class WishlistForm(FlaskForm):
    name = StringField('Wishlist name')
    is_public = BooleanField('Make Public')
    submit = SubmitField('Create a Wishlist')
