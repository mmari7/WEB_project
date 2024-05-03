from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    name = StringField("Your Friend's name", validators=[DataRequired()])
    submit = SubmitField('Show available wishlists')
