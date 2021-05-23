from flask import render_template, url_for, flash, redirect, request, abort
from GRETutoring import app, db, bcrypt
from GRETutoring.forms import RegistrationForm, LoginForm, ScheduleForm, CancellationForm, TutorRegistrationForm, UpdateAccountForm
from GRETutoring.models import User, Event, FreeSlot
from flask_login import login_user, current_user, logout_user
from flask_login import login_required
import secrets
import os
from PIL import Image
from datetime import datetime, timedelta
import calendar

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


sample_schedule_tutor_free_slots_each_day = [{"data-start": f"{i}:00", "data-end": f"{i+1}:00",
                                                  "data-content": "", "data-event": "tutor-free-slot",
                                                  "event-name": ""} for i in range(0, 24)
                                                 ]
sample_schedule_tutor_free_slots = {"Monday": ( "15 March",
                                                sample_schedule_tutor_free_slots_each_day),
                   "Tuesday": ("16 March", sample_schedule_tutor_free_slots_each_day
                       ),

                    "Wednesday": ( "17 March",
                                   sample_schedule_tutor_free_slots_each_day),
                   "Thursday": ( "18 March",
                                 sample_schedule_tutor_free_slots_each_day),
                   "Friday": ( "19 March",
                               sample_schedule_tutor_free_slots_each_day),
                   "Saturday": ( "20 March",
                                 sample_schedule_tutor_free_slots_each_day),
                   "Sunday":( "21 March",
                              sample_schedule_tutor_free_slots_each_day)}

# def login_required(role="ANY"):
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated_view(*args, **kwargs):
#
#             if not current_user.is_authenticated():
#                return app.login_manager.unauthorized()
#             urole = app.login_manager.reload_user().get_urole()
#             if ( (urole != role) and (role != "ANY")):
#                 return app.login_manager.unauthorized()
#             return fn(*args, **kwargs)
#         return decorated_view
#     return wrapper



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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='Student')
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
        student = User.query.filter_by(email=form.email.data).first()
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


def load_week(schedule, offset):
    current_day = datetime.today()
    days_to_subtract = current_day.weekday()
    current_day += timedelta(offset)
    start_of_week = current_day - timedelta(days_to_subtract)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    if current_user.role=="Tutor":
        all_classes = Event.query.filter(Event.date_time >= start_of_week, Event.date_time < (start_of_week + timedelta(7)), Event.tutor_id==current_user.id).all()
        all_free_slots = FreeSlot.query.filter(FreeSlot.date_time >= start_of_week, FreeSlot.date_time < (start_of_week + timedelta(7)), FreeSlot.tutor_id==current_user.id).all()

    else:
        all_classes = []
        all_free_slots = []

    temp = {"data-start": "14:00", "data-end": "15:15",
     "data-content": "event-yoga-1",
     "data-event": "booked-slot", "event-name": "Yoga Level 1"}

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if offset % 7 != 0:
        abort(403)
    for day in days_of_week:
        for event in all_classes:
            start_time = event.date_time
        events = schedule[day][1]
        formatted_date = (current_day - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, events)
        days_to_subtract -= 1

    return schedule



@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week(sample_schedule, offset)
    return render_template("schedule.html", title="Schedule", schedule=schedule, selected=False, offset=offset)


@app.route('/free_slots', methods=["GET", "POST"])
@login_required
def free_slots():
    if current_user.role != "Tutor":
        abort(403)
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week(sample_schedule_tutor_free_slots, offset)
    return render_template("free_slots.html", title="Free Slots", schedule=schedule, selected=False, offset=offset)


def push_free_slots_to_db(schedule):
    the_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_start = datetime.strptime(schedule["updatedSchedule"]["week_start"].strip(), "%d %b %Y")


    for slot in schedule["updatedSchedule"]["selected"]:
        day = slot["day"]
        start = slot["start"]
        end = slot["end"]
        diff = the_days.index(day)
        class_date = week_start + timedelta(diff)
        start_hour, start_minute = start.split(":")
        class_date = class_date.replace(hour=int(start_hour), minute=int(start_minute))
        class_event = FreeSlot(date_time = class_date, tutor_id = current_user.id )
        db.session.add(class_event)
        db.session.commit()

    print("Reached here")



@app.route('/add_free_slots', methods=["GET", "POST"])
@login_required
def add_free_slots():
    if current_user.role != "Tutor":
        abort(403)

    offset = int(request.args.get('offset')) if request.args.get('offset') else 0

    if request.method == 'POST':
        updated_schedule = request.get_json()
        print(updated_schedule)
        flash("Your free time slots have been updated.", "success")
        push_free_slots_to_db(updated_schedule)


    return redirect(url_for("schedule", title="Free Slots", schedule=sample_schedule, offset = offset, selected=False))



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
    if current_user.is_authenticated:
        flash(f"You already have an account as a {current_user.role.lower()}.", 'info')
        return redirect(url_for('home'))
    form = TutorRegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('A user with this email already exists. Please login if you already have an account.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            tutor = User(username=form.username.data, email=form.email.data, password=hashed_password, role='Tutor')
            db.session.add(tutor)
            db.session.commit()

            flash(f'Your application has been submitted. If we think you are a good fit, we will contact you for an interview. Thank you for your application!', 'success')
            return redirect(url_for('home'))



    return render_template("become_tutor.html", title="Register", form=form)



# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='Student')
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Account created for {form.username.data}! You are now able to login', 'success')
#         return redirect(url_for('login'))
#
#
#     return render_template("register.html", title="Register", form=form)





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
