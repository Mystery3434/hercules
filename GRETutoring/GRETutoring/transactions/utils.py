import flask_mail
import os
from GRETutoring import mail

def send_credit_purchase_email(student, num_credits):
    MY_EMAIL = os.environ.get('EMAIL_USERNAME')
    student_username = student.username
    student_email = student.email

    message_to_admin = student_username + " has purchased " + str(
        num_credits) + " credits."

    msg_admin = flask_mail.Message('Hercules credit purchase ' , sender='noreply@demo.com', recipients=[MY_EMAIL],
                                   body=message_to_admin)
    mail.send(msg_admin)

    message_to_student = f'''Hello {student_username},

You have successfully purchased {num_credits} credits. They can be viewed on your Account page. 
 
Happy studying!
Hercules Tutoring
'''
    msg_student = flask_mail.Message("Hercules Credit Purchase", sender='noreply@demo.com', recipients=[student_email], body=message_to_student)
    mail.send(msg_student)

