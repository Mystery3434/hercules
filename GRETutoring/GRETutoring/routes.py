from flask import render_template, url_for, flash, redirect, request, abort, session
from GRETutoring import app, db, bcrypt, socketio
from GRETutoring.forms import RegistrationForm, LoginForm, ScheduleForm, CancellationForm, TutorRegistrationForm, UpdateAccountForm
from GRETutoring.models import User, Event, FreeSlot, Message
from flask_login import login_user, current_user, logout_user
from flask_login import login_required
from flask_socketio import send, join_room, leave_room, rooms, emit
import secrets
import os
from PIL import Image
from datetime import datetime, timedelta
import calendar
import json

COST_PER_LESSON = 80
total_cost = 69


sample_tutors = [{"username":"Lmao", "image_file": "default.jpg", "about": "Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium"},
                 {"username":"water", "image_file":"default.jpg", "about": " Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium Lorem ipsum admen inpenium"}]

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


def load_week(schedule, offset, tutor_username):
    current_day = datetime.today()
    days_to_subtract = current_day.weekday()
    current_day += timedelta(offset)
    start_of_week = current_day - timedelta(days_to_subtract)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    all_busy_slots = []

    if current_user.role=="Tutor":
        all_classes = Event.query.filter(Event.date_time >= start_of_week, Event.date_time < (start_of_week + timedelta(7)), Event.tutor_id==current_user.id).all()
        all_free_slots = FreeSlot.query.filter(FreeSlot.date_time >= start_of_week, FreeSlot.date_time < (start_of_week + timedelta(7)), FreeSlot.tutor_id==current_user.id).all()

    else:
        tutor = User.query.filter(User.username == tutor_username).first()
        # print(tutor_username)
        # print(tutor)
        if tutor:
            all_classes = Event.query.filter(Event.date_time >= start_of_week, Event.date_time < (start_of_week + timedelta(7)), Event.tutor_id==tutor.id, Event.student_id==current_user.id).all()
            all_free_slots = FreeSlot.query.filter(FreeSlot.date_time >= start_of_week, FreeSlot.date_time < (start_of_week + timedelta(7)), FreeSlot.tutor_id==tutor.id).all()
            all_busy_slots = Event.query.filter(Event.date_time >= start_of_week, Event.date_time < (start_of_week + timedelta(7)), Event.tutor_id==tutor.id, Event.student_id!=current_user.id).all()
        else:
            all_classes = []
            all_free_slots = []



    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if offset % 7 != 0:
        abort(403)

    for day in days_of_week:
        events = schedule[day][1]
        formatted_date = (current_day - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, [])
        days_to_subtract -= 1

    temp = {"data-start": "14:00", "data-end": "15:15",
            "data-content": "event-yoga-1",
            "data-event": "booked-slot", "event-name": "Yoga Level 1"}

    for event in all_classes:
        start_time = event.date_time
        week_day =  start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, event_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min =  datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1", "data-event": "booked-slot", "event-name":"Scheduled Lesson"}
        event_list.append(event_dict)
        schedule[start_day] = (formatted_date, event_list)

    for busy_slot in all_busy_slots:
        start_time = busy_slot.date_time
        week_day =  start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, busy_slot_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min =  datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        busy_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1", "data-event": "busy-slot", "event-name":"Tutor Busy"}
        busy_slot_list.append(busy_slot_dict)
        schedule[start_day] = (formatted_date, busy_slot_list)

    for free_slot in all_free_slots:
        start_time = free_slot.date_time
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, free_slot_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        if current_user.role=="Tutor":
            free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                      "data-event": "tutor-available-slot", "event-name": "Free Slot"}
        else:
            free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                              "data-event": "free-slot", "event-name": "Free Slot"}
        free_slot_list.append(free_slot_dict)
        schedule[start_day] = (formatted_date, free_slot_list)

    print(schedule)

    return schedule




def load_week_free_slots(schedule, offset):
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


    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if offset % 7 != 0:
        abort(403)

    for day in days_of_week:
        events = schedule[day][1]
        formatted_date = (current_day - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, [])
        days_to_subtract -= 1

    temp = {"data-start": "14:00", "data-end": "15:15",
            "data-content": "event-yoga-1",
            "data-event": "booked-slot", "event-name": "Yoga Level 1"}



    all_start_times = {day:set() for day in days_of_week}

    for event in all_classes:
        start_time = event.date_time
        week_day =  start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, event_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        all_start_times[start_day].add(start_hour_min)
        end_hour_min =  datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1", "data-event": "booked-slot", "event-name":"Scheduled Lesson"}
        event_list.append(event_dict)
        schedule[start_day] = (formatted_date, event_list)

    for free_slot in all_free_slots:
        start_time = free_slot.date_time
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, free_slot_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        all_start_times[start_day].add(start_hour_min)
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                      "data-event": "tutor-selected-slot", "event-name": "Free Slot"}
        free_slot_list.append(free_slot_dict)
        schedule[start_day] = (formatted_date, free_slot_list)


    days_to_subtract = current_day.weekday()

    for day in days_of_week:
        schedule_tutor_free_slots_each_day = [{"data-start": f"{i}:00", "data-end": f"{i+1}:00",
                                               "data-content": "", "data-event": "tutor-free-slot",
                                               "event-name": ""} for i in range(0, 24) if  f"{i}:00" not in all_start_times[day] and f"0{i}:00" not in all_start_times[day]]
        events = schedule[day][1]
        events = events + schedule_tutor_free_slots_each_day
        formatted_date = (current_day - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, events)
        days_to_subtract -= 1
    print(schedule)

    return schedule


@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():
    tutor_username = request.args.get('tutor_username')
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week(sample_schedule, offset, tutor_username)
    return render_template("schedule.html", title="Schedule", tutor_username=tutor_username, schedule=schedule, selected=False, offset=offset)


@app.route('/free_slots', methods=["GET", "POST"])
@login_required
def free_slots():
    if current_user.role != "Tutor":
        abort(403)
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week_free_slots(sample_schedule_tutor_free_slots, offset)
    return render_template("free_slots.html", title="Free Slots", tutor_username=current_user.username, schedule=schedule, selected=False, offset=offset)


def push_free_slots_to_db(schedule):
    the_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_start = datetime.strptime(schedule["updatedSchedule"]["week_start"].strip(), "%d %b %Y")
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    FreeSlot.query.filter(FreeSlot.date_time >= week_start, FreeSlot.date_time < (week_start + timedelta(7)), FreeSlot.tutor_id == current_user.id).delete()
    db.session.commit()
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


def push_booked_slots_to_db(schedule, tutor_username):
    print("Entered this function successfully!")
    the_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_start = datetime.strptime(schedule["updatedSchedule"]["week_start"].strip(), "%d %b %Y")
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    tutor = User.query.filter(User.username == tutor_username).first()

    db.session.commit()
    for slot in schedule["updatedSchedule"]["selected"]:
        day = slot["day"]
        start = slot["start"]
        end = slot["end"]
        diff = the_days.index(day)
        class_date = week_start + timedelta(diff)
        start_hour, start_minute = start.split(":")
        class_date = class_date.replace(hour=int(start_hour), minute=int(start_minute))

        class_event = Event(date_time = class_date, tutor_id = tutor.id, student_id=current_user.id)

        # Delete the free slot before adding the new slot
        FreeSlot.query.filter(FreeSlot.date_time == class_date, FreeSlot.tutor_id == tutor.id).delete()

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


    return redirect(url_for("schedule", title="Free Slots", tutor_username=current_user.username, offset = offset, selected=False))


updatedSchedule={}
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    global updated_schedule
    total_cost = 0 # Temporary
    #tutor_username = request.args.get('tutor_username')
    form = ScheduleForm()
    #updated_schedule = request.args.get('updated_schedule') if request.args.get('updated_schedule') else request.get_json()

    if request.method=="POST":
        if request.get_json():
            passed_variables = request.get_json()['to_pass_to_flask']
            tutor_username = passed_variables['tutor_username']
            updated_schedule = passed_variables['updatedSchedule']
        else:
            tutor_username = request.args.get('tutor_username')

        print(updated_schedule, tutor_username)

    else:
        tutor_username = request.args.get('tutor_username')
        print(updated_schedule, tutor_username)
        # return render_template("booking.html", form=form, total_cost=total_cost, updated_schedule=updated_schedule,
        #                        tutor_username=tutor_username)



    if form.validate_on_submit():
        updated_schedule = {"updatedSchedule":updated_schedule}
        push_booked_slots_to_db(updated_schedule, tutor_username)
        flash("Your session will be booked after payment.", "success")
        return redirect(url_for('payment', updated_schedule=updated_schedule, tutor_username = tutor_username))

    return render_template("booking.html", form=form, total_cost=total_cost, updated_schedule=updated_schedule, tutor_username=tutor_username)



    # if request.method == 'POST':
    #     updated_schedule = request.get_json()
    #
    #     # number_of_lessons = len(updated_schedule['updatedSchedule']['selected'])
    #     # total_cost = COST_PER_LESSON * number_of_lessons
    #     print(updated_schedule)
    #     print(tutor_username)
    #     if form.validate_on_submit():
    #     #print(updated_schedule)
    #     #print(total_cost)
    #         push_booked_slots_to_db(updated_schedule, tutor_username)
    #         flash("Your session will be booked after payment.", "success")
    #         return redirect(url_for('payment', updated_schedule=updated_schedule, tutor_username = tutor_username))
    #
    #     #
    #     # flash("Your session will be booked after payment.", "success")
    #     # return redirect(url_for('payment', updated_schedule=updated_schedule, tutor_username = tutor_username))
    #
    #
    #
    #     #return render_template("payment.html", form=form, total_cost=total_cost)
    #
    # if request.method == 'GET':
    #     updated_schedule = request.get_json()
    #     print(updated_schedule,tutor_username )
    #     return render_template("booking.html", form=form, total_cost=total_cost)
    #
    # return render_template("booking.html", form=form, total_cost = total_cost)


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

@app.route('/booked_slot', methods=['GET', 'POST'])
def booked_slot():
    return render_template("booked_slot.html", testing_var=False)


@app.route('/payment')
def payment():
    # tutor_username = request.args.get('tutor_username')
    # updated_schedule = request.args.get('updated_schedule')
    # push_booked_slots_to_db(updated_schedule, tutor_username)
    return render_template("payment.html")

user_to_sid = {}
sid_to_user = {}
active_rooms = {}

@socketio.on("connect")
def connect():
    user_to_sid[current_user.username] = request.sid
    sid_to_user[request.sid] = current_user.username
    active_rooms[current_user.username] = []
    print("Just connected: " , user_to_sid)

@socketio.on("message")
def handle_message(data):
    print("Message: " + data["text"])
    target_username = data["target_username"]
    source_username = data["source_username"]
    print(f"Sent from {source_username} to {target_username}")
    participants = sorted([source_username, target_username])
    room = user_to_sid[participants[0]] + user_to_sid[participants[1]]

    sender_id = User.query.filter_by(username=source_username).first().id
    recipient_id = User.query.filter_by(username=target_username).first().id

    message = Message(message_text=data["text"], date_time = datetime.now(), sender_id=sender_id, recipient_id=recipient_id)

    db.session.add(message)
    db.session.commit()

    # send(data["text"], to=user_to_sid[source_username])
    # send(data["text"], to=user_to_sid[target_username])
    send(data, to=room)


@socketio.on('join')
def on_join(data):
    source_username = data['source_username']
    target_username = data['target_username']
    # user_to_sid[current_user.username] = request.sid
    # sid_to_user[request.sid] = current_user.username

    print(user_to_sid)
    participants = sorted([source_username, target_username])
    room = user_to_sid[participants[0]] + user_to_sid[participants[1]]
    active_rooms[current_user.username].append(room)
    join_room(room)
    # emit("message", source_username + ' and ' + target_username + ' have entered the room.', to=room)

    sender_id = User.query.filter_by(username=source_username).first().id
    recipient_id = User.query.filter_by(username=target_username).first().id

    # Load all the messages that the two users had with each other
    messages_to_load = Message.query.filter_by(sender_id=sender_id, recipient_id=recipient_id).all()
    messages_to_load += Message.query.filter_by(sender_id=recipient_id, recipient_id=sender_id).all()

    messages_to_load.sort(key=lambda x:x.date_time)
    print(messages_to_load)

    messages_to_pass = []
    for message in messages_to_load:
        message_to_pass = message.asdict()
        message_to_pass["sender_username"] = User.query.filter_by(id=message_to_pass["sender_id"]).first().username
        message_to_pass["recipient_username"] = User.query.filter_by(id=message_to_pass["recipient_id"]).first().username
        message_to_pass["date_time"] = message_to_pass["date_time"].strftime("%H:%M")
        messages_to_pass.append(message_to_pass)

    print(messages_to_pass)
    emit('new_private_message', messages_to_pass, room=room)


@socketio.on('leave')
def on_leave(data):
    print(active_rooms[current_user.username])
    source_username = data['source_username']
    for room in active_rooms[source_username]:
        leave_room(room)

    # for user, sid in user_to_sid.items():
    #     if source_username != user:
    #         target_username = user
    #         participants = sorted([source_username, target_username])
    #         room = user_to_sid[participants[0]] + user_to_sid[participants[1]]
    #         leave_room(room)
    #         send(source_username + ' has left the room.', to=room)




@app.route('/message')
@login_required
def message():
    associated_classes = current_user.student_classes if current_user.role=="Student" else current_user.tutor_classes
    if current_user.role=="Student":
        associated_users = set([event.tutor_id for event in associated_classes])
    else:
        associated_users = set([event.student_id for event in associated_classes])

    associated_usernames = []
    associated_image_files = []
    user_dict = {}
    users_list = []
    for id in associated_users:
        associated_user = User.query.filter(User.id==id).first()
        user_dict["username"] = associated_user.username
        user_dict["image_file"] = url_for('static', filename="profile_pics/" + associated_user.image_file)
        received_messages = Message.query.filter_by(sender_id=associated_user.id, recipient_id=current_user.id).all()
        received_messages += Message.query.filter_by(sender_id=current_user.id, recipient_id=associated_user.id).all()
        received_messages.sort(key=lambda x:x.date_time)
        user_dict["last_received_message"] = "" if not received_messages else received_messages[-1].message_text
        if len(user_dict["last_received_message"]) >= 20:
            user_dict["last_received_message"] = user_dict["last_received_message"][:20] + "..."
        users_list.append(user_dict)
        user_dict = {}



    return render_template("message.html", users = users_list, users_json=json.dumps(users_list))

@app.route('/find_tutor')
@login_required
def find_tutor():
    if current_user.role == "Tutor":
        abort(403)
    page = request.args.get('page', 1, type=int)
    tutors = User.query.filter_by(role="Tutor").paginate(page=page, per_page=5)

    return render_template("find_tutor.html", tutors=tutors)

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
        if form.about.data:
            current_user.about = form.about.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about.data = current_user.about

    image_file = url_for('static', filename="profile_pics/" + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)
