from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField,  TextAreaField
from wtforms.validators import  DataRequired, Length, Email


class ContactUsForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email() ])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')