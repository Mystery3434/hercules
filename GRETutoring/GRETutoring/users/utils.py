from flask import url_for, current_app
from GRETutoring import mail

import secrets
import os
from PIL import Image

import flask_mail



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = flask_mail.Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body=f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request, then simply ignore this email and no change will be made.
    '''
    mail.send(msg)


def send_account_opening_email(student):
    MY_EMAIL = os.environ.get('EMAIL_USERNAME')
    student_email = student.email
    student_username = student.username
    msg_admin = flask_mail.Message('New Student Registration', sender='noreply@demo.com', recipients=[MY_EMAIL])
    msg_admin.body= f"A new student {student_username}, with email: {student_email} has registered on Hercules."
    mail.send(msg_admin)
    msg_student = flask_mail.Message('Hercules New Account Opening', sender='noreply@demo.com', recipients=[student_email])
    msg_student.body = f'''Hello,

Thank you for registering with Hercules Tutoring! We are pleased that you have chosen Hercules for your GRE Tutoring lessons.

You can now click on "Find a Tutor" when logged in to your account to browse the list of available tutors. Feel free to book a lesson with any tutor that catches your interest. 

To schedule a lesson, you will need to purchase lesson credits on the "Buy Credits" page. 1 Credit = 1 Hour of lessons. As a new user, you will receive 80% off on your first credit. 

Happy studying!

Best regards,
Hercules Tutoring

    '''
    mail.send(msg_student)



def send_tutor_registration_email(tutor_email):
    msg = flask_mail.Message('New Tutor Registration', sender='noreply@demo.com', recipients=[tutor_email])
    msg.body=f'''Hello,
    
Thank you for registering with Hercules Tutoring! We have received your application and will get in touch with you shortly for an interview if you are a good fit for our position.
    
Best regards,
Hercules Tutoring

    '''
    mail.send(msg)


def send_tutor_registration_admin_email(tutor_form):
    MY_EMAIL = os.environ.get('EMAIL_USERNAME')
    name = tutor_form.name.data
    username = tutor_form.username.data
    email = tutor_form.email.data
    verbal_score = tutor_form.verbal_score.data
    quant_score = tutor_form.quant_score.data
    awa_score = tutor_form.awa_score.data
    video_link = tutor_form.video_link.data
    time_zone = tutor_form.time_zone.data
    misc_info = tutor_form.misc_info.data

    msg = flask_mail.Message('New Tutor Registration', sender='noreply@demo.com', recipients=[MY_EMAIL])
    msg.body = f'''{name} (username : {username}) would like to become a tutor. Their email is {email}. Their scores are:
    
    Quant: {quant_score}
    Verbal: {verbal_score}
    AWA: {awa_score}
    
    Video link for the tutor: {video_link}
    
    The tutor's time zone is {time_zone}. 
    
    Addtional info that the tutor has provided: 
    {misc_info}
    
    '''
    mail.send(msg)


def send_review_notification(tutor):
    username = tutor.username
    email = tutor.email

    msg = flask_mail.Message('New Tutor Review', sender='noreply@demo.com', recipients=[email])
    msg.body = f'''Hello {username},

You have received a review from a student. To view the review, go to Account -> View my profile.

Happy teaching!

    '''
    mail.send(msg)