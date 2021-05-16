from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import  DataRequired, Length, Email, EqualTo, Optional, NumberRange, URL, ValidationError
from GRETutoring.models import Student
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('That username is already taken. Please choose another one.')

    def validate_email(self, email):

        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('There is already an account with that email. Please login instead.')



class TutorRegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    verbal_score = SelectField(u'Verbal Reasoning Score', coerce=int, choices=[(0, "")] + [(i, i) for i in range(163, 171)], validators=[NumberRange(min=163, max=170, message="Your score must be at least 166 to be considered. We do make some exceptions for scores below that, but it has to be above 163.")])
    quant_score = SelectField(u'Quantitative Reasoning Score', coerce=int, choices=[(0, "")] + [(i, i) for i in range(163, 171)], validators=[NumberRange(min=163, max=170, message="Your score must be at least 166 to be considered. We do make some exceptions for scores below that, but it has to be above 163.")])
    awa_score = SelectField(u'Analytical Writing Score', coerce=float, choices=[(0, "")] + [(i, i) for i in [5.0, 5.5, 6.0]], validators=[NumberRange(min=5.0, max=6.0, message="Your score must be at least 5.5 to be considered. We do make some exceptions for scores below that, but it has to be above 5.0.")])
    video_link = StringField('Please submit a short video (under 2 minutes) about why you would like to join Hercules. You can include any details you think are necessary. Please submit the video link here. We recommend using a YouTube link.', validators=[URL(), Length(max=250)])
    submit = SubmitField('Submit Tutor Application')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ScheduleForm(FlaskForm):
    quant = BooleanField('Quantitative Reasoning')
    verbal = BooleanField('Verbal Reasoning')
    awa = BooleanField('Analytical Writing')
    special_requests = TextAreaField('Special Requests', validators = [Optional(), Length(max=200)])
    book = SubmitField('Book')

class CancellationForm(FlaskForm):
    reasons = TextAreaField('Reason(s) for cancellation: ', validators = [DataRequired(), Length(max=200)])
    cancel = SubmitField('Cancel')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            student = Student.query.filter_by(username=username.data).first()
            if student:
                raise ValidationError('That username is already taken. Please choose another one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            student = Student.query.filter_by(email=email.data).first()
            if student:
                raise ValidationError('There is already an account with that email. Please login instead.')
