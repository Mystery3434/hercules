from flask import Blueprint

from flask import render_template, url_for, flash, redirect
from flask import current_app as app
from GRETutoring import mail
from GRETutoring.main.forms import ContactUsForm
import flask_mail


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template("home.html")


@main.route('/about')
def about():
    return render_template("about.html")


@main.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    with app.app_context():
        MY_EMAIL = app.config['MAIL_USERNAME']

    form = ContactUsForm()
    if form.validate_on_submit():
        email = form.email.data
        message_text = form.message.data
        msg = flask_mail.Message('Hercules Customer Support', sender=MY_EMAIL, recipients=[MY_EMAIL])
        msg.body = message_text + "\nSender: " + email
        mail.send(msg)
        flash('Your message has been sent. We will reply to you as soon as we can.', 'success')
        return redirect(url_for('main.home'))

    return render_template("contact_us.html", title="Contact Us", form=form)