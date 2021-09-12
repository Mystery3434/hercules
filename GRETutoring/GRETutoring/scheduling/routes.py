from flask import Blueprint
from GRETutoring.scheduling.utils import load_week, load_week_free_slots, push_free_slots_to_db, push_booked_slots_to_db

from flask import render_template, url_for, flash, redirect, request, abort
from GRETutoring.scheduling.forms import ScheduleForm, CancellationForm

from flask_login import current_user
from flask_login import login_required



scheduling = Blueprint('scheduling', __name__)



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




@scheduling.route('/scheduling', methods=["GET", "POST"])
@login_required
def schedule():
    tutor_username = request.args.get('tutor_username')
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week(sample_schedule, offset, tutor_username)
    return render_template("schedule.html", title="Schedule", tutor_username=tutor_username, schedule=schedule, selected=False, offset=offset)


@scheduling.route('/free_slots', methods=["GET", "POST"])
@login_required
def free_slots():
    if current_user.role != "Tutor":
        abort(403)
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week_free_slots(sample_schedule_tutor_free_slots, offset)
    return render_template("free_slots.html", title="Free Slots", tutor_username=current_user.username, schedule=schedule, selected=False, offset=offset)


@scheduling.route('/add_free_slots', methods=["GET", "POST"])
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


    return redirect(url_for("scheduling.schedule", title="Free Slots", tutor_username=current_user.username, offset = offset, selected=False))


updatedSchedule={}
@scheduling.route('/booking', methods=['GET', 'POST'])
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
        return redirect(url_for('transactions.payment', updated_schedule=updated_schedule, tutor_username = tutor_username))

    return render_template("booking.html", form=form, total_cost=total_cost, updated_schedule=updated_schedule, tutor_username=tutor_username)



@scheduling.route('/cancel_booking', methods=['GET', 'POST'])
def cancel_booking():
    form = CancellationForm()
    if form.validate_on_submit():
        flash('Cancellation request sent', 'success')
        return redirect(url_for('main.home'))

    return render_template("cancel_booking.html", form=form)


@scheduling.route('/available_slot')
def available_slot():
    return render_template("available_slot.html", testing_var=False)


@scheduling.route('/selected_slot')
def selected_slot():
    return render_template("selected_slot.html", testing_var=False)

@scheduling.route('/busy_slot')
def busy_slot():
    return render_template("busy_slot.html", testing_var=False)

@scheduling.route('/past_slot')
def past_slot():
    return render_template("past_slot.html", testing_var=False)

@scheduling.route('/booked_slot', methods=['GET', 'POST'])
def booked_slot():
    return render_template("booked_slot.html", testing_var=False)
