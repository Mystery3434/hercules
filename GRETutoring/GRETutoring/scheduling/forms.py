from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, TextAreaField
from wtforms.validators import  DataRequired, Length, Optional

class ScheduleForm(FlaskForm):
    quant = BooleanField('Quantitative Reasoning')
    verbal = BooleanField('Verbal Reasoning')
    awa = BooleanField('Analytical Writing')
    special_requests = TextAreaField('Special Requests', validators = [Optional(), Length(max=200)])
    book = SubmitField('Book')

class CancellationForm(FlaskForm):
    reasons = TextAreaField('Reason(s) for cancellation: ', validators = [DataRequired(), Length(max=200)])
    cancel = SubmitField('Cancel')

class RescheduleForm(FlaskForm):
    reasons = TextAreaField('Reason(s) for rescheduling: ', validators = [DataRequired(), Length(max=200)])
    reschedule = SubmitField('Reschedule')
