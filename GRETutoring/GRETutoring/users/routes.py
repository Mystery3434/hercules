from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from GRETutoring import db, bcrypt
from GRETutoring.users.forms import RegistrationForm, LoginForm, TutorRegistrationForm, UpdateAccountForm, ReviewForm, RequestResetForm, ResetPasswordForm
from GRETutoring.models import User, Review, Event, TutorApplication

from GRETutoring.users.utils import save_picture, send_reset_email, send_tutor_registration_email, send_tutor_registration_admin_email, send_review_notification, send_account_opening_email

from flask_login import login_user, current_user, logout_user
from flask_login import login_required

from datetime import datetime
import pytz

from GRETutoring import mail
import flask_mail


users = Blueprint('users', __name__)


sample_tutors = [{"username":"Lmao", "image_file": "default.jpg", "about": "Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium"},
                 {"username":"water", "image_file":"default.jpg", "about": " Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium"}]



@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='Student', time_zone=form.time_zone.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You are now able to login', 'success')

        email = form.email.data
        send_account_opening_email(user)
        # message_text = "The user " + form.username.data + " with the email ID " + email + " has created a new account on Hercules."
        # msg = flask_mail.Message('New user registered on Hercules', sender='noreply@demo.com', recipients=[MY_EMAIL])
        # msg.body = message_text
        # mail.send(msg)

        return redirect(url_for('users.login'))




    return render_template("register.html", title="Register", form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role=="Pending":
            flash('Login Unsuccessful. Your application is still pending approval.', 'warning')
        elif user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template("login.html", title="Login", form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.skype_id = form.skype_id.data
        current_user.hangouts_id = form.hangouts_id.data
        current_user.time_zone = form.time_zone.data
        if form.about.data:
            current_user.about = form.about.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about.data = current_user.about
        form.skype_id.data = current_user.skype_id
        form.hangouts_id.data  = current_user.hangouts_id
        form.time_zone.data = current_user.time_zone

    image_file = url_for('static', filename="profile_pics/" + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/find_tutor')
@login_required
def find_tutor():
    if current_user.role == "Tutor":
        abort(403)
    page = request.args.get('page', 1, type=int)
    tutors = User.query.filter_by(role="Tutor").paginate(page=page, per_page=5)

    for tutor in tutors.items:
        tutor.num_lessons = len(Event.query.filter_by(tutor_id = tutor.id).all())

    return render_template("find_tutor.html", tutors=tutors)

@users.route('/become_tutor', methods=['GET', 'POST'])
def become_tutor():
    if current_user.is_authenticated:
        flash(f"You already have an account as a {current_user.role.lower()}.", 'info')
        return redirect(url_for('main.home'))
    form = TutorRegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('A user with this email already exists. Please login if you already have an account.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            tutor = User(username=form.username.data, email=form.email.data, password=hashed_password, role='Pending', time_zone=form.time_zone.data)
            db.session.add(tutor)
            db.session.commit()
            tutor_application = TutorApplication(tutor_id = tutor.id, username = tutor.username, email = tutor.email, date_time = datetime.utcnow(),
                                                 verbal_score = form.verbal_score.data, quant_score = form.quant_score.data, awa_score = form.awa_score.data,
                                                 video_link = form.video_link.data, misc_info = form.misc_info.data, time_zone = form.time_zone.data)
            db.session.add(tutor_application)
            db.session.commit()
            send_tutor_registration_email(form.email.data)
            send_tutor_registration_admin_email(form)
            flash(f'Your application has been submitted. If we think you are a good fit, we will contact you for an interview. Thank you for your application!', 'success')
            return redirect(url_for('main.home'))



    return render_template("become_tutor.html", title="Register", form=form)


@login_required
@users.route('/pending_tutor_applications', methods=['GET', 'POST'])
def pending_tutor_applications():
    if current_user.role != "Admin":
        abort(403)
    if request.method=="GET":
        page = request.args.get('page', 1, type=int)
        # tutors = User.query.filter_by(role="Tutor").paginate(page=page, per_page=5)
        pending_tutors = TutorApplication.query.paginate(page=page, per_page=5)
        return render_template("pending_tutor_applications.html", tutors=pending_tutors)
    else:
        if request.get_json():
            approved_application_id = request.get_json()['approved_application_id']["application_id"]
            approved_application = TutorApplication.query.filter_by(id=approved_application_id).first()
            approved_tutor = User.query.filter_by(id=approved_application.tutor_id).first()
            approved_tutor.role="Tutor"
            db.session.delete(approved_application)
            db.session.add(approved_tutor)
            db.session.commit()
            flash(f"Successfully approved tutor", "success")
            # page = request.args.get('page', 1, type=int)
            # pending_tutors = TutorApplication.query.paginate(page=page, per_page=5)
        return redirect(url_for("users.pending_tutor_applications"))


@users.route('/view_profile', methods=['GET', 'POST'])
def view_profile():
    username = request.args.get('username')
    is_current_tutor = False
    already_reviewed = False

    associated_classes = current_user.student_classes if current_user.role == "Student" else []
    if current_user.role == "Student":
        associated_users = set([event.tutor_id for event in associated_classes])
    else:
        associated_users = set([])

    user = User.query.filter_by(username=username).first()

    if not user:
        abort(404)

    if user.id in associated_users:
        is_current_tutor = True


    image_file = url_for('static', filename="profile_pics/" + user.image_file)

    tz = pytz.timezone(current_user.time_zone)

    reviews = Review.query.filter_by(tutor_id=user.id).all()
    review_list = []
    for review in reversed(reviews):
        review = review.asdict()
        review['student_username'] = User.query.filter_by(id=review["student_id"]).first().username
        if review['student_username'] == current_user.username:
            already_reviewed = True
        review['student_image_file'] = User.query.filter_by(id=review["student_id"]).first().image_file
        review['formatted_date_time'] = datetime.strftime(tz.fromutc(review["date_time"]), "%d %B %Y")
        #review['review_score'] -= 0.5
        review['whole_stars'] = int(review['review_score'])
        review['half_stars'] = 0 if review['review_score'] - review['whole_stars'] == 0 else 1
        review['grey_stars'] = 5 - int(review['review_score'] + 0.5)
        review_list.append(review)

    profile_type = user.role
    num_lessons = len(Event.query.filter_by(tutor_id = user.id).all())
    return render_template('view_profile.html', title='View Profile', already_reviewed=already_reviewed, num_lessons=num_lessons, image_file=image_file, user=user, reviews=review_list, is_current_tutor=is_current_tutor, profile_type=profile_type)


@users.route('/add_review', methods=['GET', 'POST'])
@login_required
def add_review():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(403)
    if current_user.role == "Tutor":
        abort(403)

    # Ensure that students who are not tutored by the tutor can't add reviews
    classes = Event.query.filter_by(student_id=current_user.id, tutor_id=user.id).all()
    if not classes:
        abort(403)

    image_file = url_for('static', filename="profile_pics/" + user.image_file)
    form = ReviewForm()
    existing_review = Review.query.filter(Review.student_id == current_user.id, Review.tutor_id==user.id).first()
    if form.validate_on_submit():
        if not existing_review:
            review = Review(review_text=form.review.data, review_score=form.score.data, date_time=datetime.utcnow(), student_id=current_user.id, tutor_id = user.id)
            db.session.add(review)
            db.session.commit()
            send_review_notification(user)

        else:
            existing_review.review_text=form.review.data
            existing_review.review_score = form.score.data
            existing_review.date_time = datetime.utcnow()
            db.session.commit()

        flash('Your review has been submitted!', 'success')
        return redirect(url_for('users.view_profile', username=username))
    elif request.method == 'GET':

        if existing_review:
            form.score.data = existing_review.review_score
            print(form.score.data)
            form.review.data = existing_review.review_text

    return render_template('add_review.html', user=user, image_file=image_file, form=form, title='Add Review')




@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Your password has now been updated! You are now able to login', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title="Reset Password", form=form)


