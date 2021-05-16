from flask import render_template, url_for, flash, redirect, request
from GRETutoring import app, db, bcrypt
from GRETutoring.forms import RegistrationForm, LoginForm, ScheduleForm, CancellationForm, TutorRegistrationForm, UpdateAccountForm
from GRETutoring.models import Student, Tutor, Event
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image

COST_PER_LESSON = 80
total_cost = 69

sample_schedule = {"Monday": ( "15 March",
                       [{"data-start":"09:30", "data-end":"10:30", "data-content":"event-abs-circuit", "data-event":"booked-slot", "event-name":"Booked Slot"},
                        {"data-start": "10:30", "data-end": "11:00", "data-content": "event-rowing-workout",
                         "data-event": "free-slot", "event-name": "Available Slot"},
                        {"data-start": "11:00", "data-end": "12:30", "data-content": "event-rowing-workout",
                         "data-event": "event-2", "event-name": "Rowing Workout"},
                        {"data-start": "14:00", "data-end": "15:15", "data-content": "event-yoga-1",
                         "data-event": "event-3", "event-name": "Yoga Level 1"}]),
                   "Tuesday": ("16 March",
                       [
                           {"data-start": "10:00", "data-end": "11:00", "data-content": "event-rowing-workout",
                            "data-event": "event-2", "event-name": "Rowing Workout"},
                            {"data-start": "11:30", "data-end": "13:00", "data-content": "event-restorative-yoga",
                            "data-event": "event-4", "event-name": "Restorative Yoga"},
                            {"data-start": "13:30", "data-end": "15:00", "data-content": "event-abs-circuit",
                            "data-event": "booked-slot", "event-name": "Booked Slot"},
                           {"data-start": "15:45", "data-end": "16:45", "data-content": "event-yoga-1",
                            "data-event": "event-3", "event-name": "Yoga Level 1"}
                       ]),

                    "Wednesday": ( "17 March",
                                   [
                                       {"data-start": "9:00", "data-end": "10:15",
                                        "data-content": "event-restorative-yoga",
                                        "data-event": "event-4", "event-name": "Restorative Yoga"},
                                       {"data-start": "10:45", "data-end": "11:45",
                                        "data-content": "event-yoga-1",
                                        "data-event": "event-3", "event-name": "Yoga Level 1"},
                                        {"data-start": "12:00", "data-end": "13:45",
                                        "data-content": "event-rowing-workout",
                                        "data-event": "event-2", "event-name": "Rowing Workout"},
                                        {"data-start": "13:45", "data-end": "15:00",
                                        "data-content": "event-yoga-1",
                                        "data-event": "event-3", "event-name": "Yoga Level 1"},

                                   ]),
                   "Thursday": ( "18 March",
                                   [
{"data-start": "09:30", "data-end": "10:30",
                                        "data-content": "event-abs-circuit",
                                        "data-event": "busy-slot", "event-name": "No Tutors Available"},
{"data-start": "10:30", "data-end": "11:00",
                                        "data-content": "event-abs-circuit",
                                        "data-event": "free-slot", "event-name": "Available Slot"},
{"data-start": "11:00", "data-end": "11:30",
                                        "data-content": "event-abs-circuit",
                                        "data-event": "free-slot", "event-name": "Available Slot"},
{"data-start": "12:00", "data-end": "13:45",
                                        "data-content": "event-restorative-yoga",
                                        "data-event": "event-4", "event-name": "Restorative Yoga"},
{"data-start": "15:30", "data-end": "16:30", "data-content": "event-abs-circuit",
                            "data-event": "event-1", "event-name": "Abs Circuit"},
{"data-start": "17:00", "data-end": "18:30",
                                        "data-content": "event-rowing-workout",
                                        "data-event": "event-2", "event-name": "Rowing Workout"}
                                   ]),
                   "Friday": ( "19 March",
                                   [
{"data-start": "10:00", "data-end": "11:00",
                                        "data-content": "event-rowing-workout",
                                        "data-event": "event-2", "event-name": "Rowing Workout"},
{"data-start": "12:30", "data-end": "14:00", "data-content": "event-abs-circuit",
                            "data-event": "busy-slot", "event-name": "No Tutors Available"},
{"data-start": "15:45", "data-end": "16:45",
                                        "data-content": "event-yoga-1",
                                        "data-event": "event-3", "event-name": "Yoga Level 1"}
                                   ]),
                   "Saturday": ( "20 March",
                                   [
{"data-start": "09:30", "data-end": "10:30", "data-content": "event-abs-circuit",
                            "data-event": "event-1", "event-name": "Abs Circuit"},
{"data-start": "11:00", "data-end": "12:30",
                                        "data-content": "event-rowing-workout",
                                        "data-event": "event-2", "event-name": "Rowing Workout"},
{"data-start": "14:00", "data-end": "15:15",
                                        "data-content": "event-yoga-1",
                                        "data-event": "event-3", "event-name": "Yoga Level 1"}
                                   ]),
                   "Sunday":( "21 March",
                                   [
{"data-start": "09:30", "data-end": "10:30", "data-content": "event-abs-circuit",
                            "data-event": "event-1", "event-name": "Abs Circuit"},
{"data-start": "11:00", "data-end": "12:30",
                                        "data-content": "event-rowing-workout",
                                        "data-event": "event-2", "event-name": "Rowing Workout"},
{"data-start": "14:00", "data-end": "15:15",
                                        "data-content": "event-yoga-1",
                                        "data-event": "event-3", "event-name": "Yoga Level 1"}
                                   ])}




@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Student(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You are now able to login', 'success')
        return redirect(url_for('login'))


    return render_template("register.html", title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data).first()
        if student and bcrypt.check_password_hash(student.password, form.password.data):
            login_user(student, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template("login.html", title="Login", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/schedule', methods=["GET", "POST"])
def schedule():
    return render_template("schedule.html", title="Schedule", schedule=sample_schedule, selected=False)



@app.route('/booking', methods=['GET', 'POST'])
def booking():
    global total_cost
    form = ScheduleForm()
    if form.validate_on_submit():

        flash('Please complete the payment', 'success')
        return redirect(url_for('payment'))

    if request.method == 'POST':
        updated_schedule = request.get_json()
        number_of_lessons = len(updated_schedule['updatedSchedule']['selected'])
        total_cost = COST_PER_LESSON * number_of_lessons
        print(updated_schedule)
        print(total_cost)
        return render_template("booking.html", form=form, total_cost=total_cost)

    if request.method == 'GET':
        return render_template("booking.html", form=form, total_cost=total_cost)

    return render_template("booking.html", form=form, total_cost = total_cost)


@app.route('/cancel_booking', methods=['GET', 'POST'])
def cancel_booking():
    form = CancellationForm()
    if form.validate_on_submit():
        flash('Cancellation request sent', 'success')
        return redirect(url_for('home'))

    return render_template("cancel_booking.html", form=form)


@app.route('/available_slot')
def available_slot():
    return render_template("available_slot.html", testing_var=False)


@app.route('/selected_slot')
def selected_slot():
    return render_template("selected_slot.html", testing_var=False)

@app.route('/busy_slot')
def busy_slot():
    return render_template("busy_slot.html", testing_var=False)

@app.route('/booked_slot')
def booked_slot():
    return render_template("booked_slot.html", testing_var=False)


@app.route('/payment')
def payment():
    return render_template("payment.html")

@app.route('/message')
def message():
    return render_template("message.html")

@app.route('/become_tutor', methods=['GET', 'POST'])
def become_tutor():
    form = TutorRegistrationForm()
    if form.validate_on_submit():
        flash(f'Your application has been submitted. If we think you are a good fit, we will contact you for an interview. Thank you for your application!', 'success')
        return redirect(url_for('home'))


    return render_template("become_tutor.html", title="Register", form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename="profile_pics/" + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)
