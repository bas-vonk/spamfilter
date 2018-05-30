from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    """
    This is the flask form object for the search fields.
    """

    query = StringField('Query', validators=[DataRequired()])
    submit = SubmitField('Search!')
