from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, RadioField
from wtforms.validators import  DataRequired, Optional, Length, Email, EqualTo, NumberRange, URL, ValidationError
from wtforms.widgets import TextArea
from GRETutoring.models import User
from flask_login import current_user
import pytz

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    time_zone = SelectField(u'Timezone', coerce=str,
                            choices=[("", "")] + [(x, x) for x in pytz.common_timezones],  validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        student = User.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('That username is already taken. Please choose another one.')

    def validate_email(self, email):

        student = User.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('There is already an account with that email. Please login instead.')




class TutorRegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    verbal_score = SelectField(u'Verbal Reasoning Score', coerce=int, choices=[(0, "")] + [(i, i) for i in range(163, 171)], validators=[NumberRange(min=163, max=170, message="Your score must be at least 166 to be considered. We do make some exceptions for scores below that, but it has to be above 163.")])
    quant_score = SelectField(u'Quantitative Reasoning Score', coerce=int, choices=[(0, "")] + [(i, i) for i in range(163, 171)], validators=[NumberRange(min=163, max=170, message="Your score must be at least 166 to be considered. We do make some exceptions for scores below that, but it has to be above 163.")])
    awa_score = SelectField(u'Analytical Writing Score', coerce=float, choices=[(0, "")] + [(i, i) for i in [5.0, 5.5, 6.0]], validators=[NumberRange(min=5.0, max=6.0, message="Your score must be at least 5.5 to be considered. We do make some exceptions for scores below that, but it has to be above 5.0.")])
    video_link = StringField('Please submit a short video (under 2 minutes) about why you would like to join Hercules. You can include any details you think are necessary. Please submit the video link here. We recommend using a YouTube link.', validators=[URL(), Length(max=250), DataRequired()])
    time_zone = SelectField(u'Which timezone are you currently located in?', coerce=str,
                            choices=[("", "")] + [(x, x) for x in pytz.common_timezones], validators=[DataRequired()])
    misc_info = StringField(u'Is there any additional information that you would like to provide us that could support your application?', validators=[Length(max=250)],  widget=TextArea())
    submit = SubmitField('Submit Tutor Application')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ReviewForm(FlaskForm):
    score = RadioField('Score', choices=[ (val, desc) for desc, val in [('Perfect', 5.0),('Almost Perfect', 4.5), ('Very Good', 4.0), ('Good', 3.5), ('Satisfactory', 3.0), ('Some improvement required', 2.5),
        ('Lots of improvement required', 2.0), ('Bad', 1.5), ('Very Bad', 1.0), ('Terrible', 0.5)]],
                       validators=[DataRequired()], coerce=float
        )
    review = TextAreaField(
        'Review:',
        validators=[Length(max=1500), DataRequired()], render_kw={"placeholder": "Enter review here"})
    submit = SubmitField('Submit Review')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    skype_id = StringField('Skype ID', validators=[Length(min=0, max=50)])
    hangouts_id = StringField('Hangouts ID', validators=[Length(min=0, max=50)])
    paypal_info = StringField('Paypal Email', validators=[Optional(),Email()])
    about = TextAreaField('Enter a short bio talking about you and your teaching style. Include anything that you think is relevant for your students.',
                          validators=[Length(max=1500)])
    time_zone = SelectField(u'Timezone', coerce=str,
                            choices=[("", "")] + [(x, x) for x in pytz.common_timezones],  validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            student = User.query.filter_by(username=username.data).first()
            if student:
                raise ValidationError('That username is already taken. Please choose another one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            student = User.query.filter_by(email=email.data).first()
            if student:
                raise ValidationError('There is already an account with that email. Please login instead.')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
