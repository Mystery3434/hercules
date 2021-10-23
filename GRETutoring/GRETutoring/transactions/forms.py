from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, RadioField
from wtforms.validators import  DataRequired, Length, Email, EqualTo, NumberRange, URL, ValidationError
from GRETutoring.models import User
from flask_login import current_user
import pytz

class BuyCreditsForm(FlaskForm):
    num = IntegerField()
    submit = SubmitField('Buy Now')