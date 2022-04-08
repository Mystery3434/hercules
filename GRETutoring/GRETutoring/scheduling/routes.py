from flask import Blueprint
from GRETutoring.scheduling.utils import load_week, load_week_free_slots, push_free_slots_to_db, push_booked_slots_to_db, load_student_schedule, get_slot_to_cancel, cancel_slot, send_scheduling_emails, scheduling_conflict, RescheduleRequests, user_time, get_slot_to_reschedule, get_slot_to_add, add_slot, check_reschedule_request_safety, create_slot

from flask import render_template, url_for, flash, redirect, request, abort
from GRETutoring.scheduling.forms import ScheduleForm, CancellationForm, RescheduleForm


from GRETutoring.models import User

from flask_login import current_user
from flask_login import login_required

from datetime import datetime
import pytz


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

@scheduling.route('/student_schedule', methods=["GET", "POST"])
@login_required
def student_schedule():

    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_student_schedule(sample_schedule, offset)
    return render_template("student_schedule.html", title="Schedule", schedule=schedule, selected=False, offset=offset)



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
        # print(updated_schedule)
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

                #return render_template(url_for('scheduling.schedule'), title="Schedule", tutor_username=tutor_username, schedule=schedule, selected=False, offset=0)
        else:
            tutor_username = request.args.get('tutor_username')

    else:
        tutor_username = request.args.get('tutor_username')
        #print(updated_schedule, tutor_username)
        # return render_template("booking.html", form=form, total_cost=total_cost, updated_schedule=updated_schedule,
        #                        tutor_username=tutor_username)

    num_lessons = len(updated_schedule.get('selected'))
    if num_lessons > current_user.credits:
        flash("You do not have enough credits for your selected booking. 1 credit = 1 hour of class.", 'danger')
        # print("num greater")
        return redirect(
                url_for("scheduling.schedule", title="Schedule", tutor_username=tutor_username, offset=0,
                        selected=False))

    elif num_lessons == 0:
        flash("You have not selected any slots to book.", 'danger')
        # print("num zero")
        return redirect(
                url_for("scheduling.schedule", title="Schedule", tutor_username=tutor_username, offset=0,
                        selected=False))

    elif scheduling_conflict(updated_schedule):

        #print("TESTING UPATED SCHEDULE", updated_schedule)
        flash("You have a time conflict with the selected classes.", 'danger')
        return redirect(
            url_for("scheduling.schedule", title="Schedule", tutor_username=tutor_username, offset=0,
                    selected=False))

    if form.validate_on_submit():
        updated_schedule = {"updatedSchedule":updated_schedule}
        # print(updated_schedule)

        push_booked_slots_to_db(updated_schedule, tutor_username)

        send_scheduling_emails("booking", num_lessons, tutor_username, form)

        #flash("Your session will be booked after payment.", "success")
        return redirect(url_for('scheduling.successful_booking', updated_schedule=updated_schedule, tutor_username = tutor_username))

    return render_template("booking.html", form=form, updated_schedule=updated_schedule, tutor_username=tutor_username)


@scheduling.route('/successful_booking')
def successful_booking():
    return render_template("successful_booking.html")



lesson_to_cancel = None
@scheduling.route('/cancel_booking', methods=['GET', 'POST'])
def cancel_booking():
    form = CancellationForm()
    global lesson_to_cancel


    if request.method=="POST":
        if request.get_json():
            passed_variables = request.get_json()['to_pass_to_flask']
            date_text = passed_variables['date_text']
            date_text = date_text.strip().split("\n")
            # print(date_text[0].strip(), date_text[-2].strip()  )
            # print(date_text)
            day = date_text[0].strip()
            start_time = passed_variables['class_start'].strip()
            # print(day)
            # print(start_time)
            time_to_cancel = datetime.strptime(day + " " + start_time, '%d %b %Y %H:%M')
            # print(time_to_cancel)
            lesson_to_cancel = get_slot_to_cancel(time_to_cancel)


        #return render_template("cancel_booking.html", form=form)

    if form.validate_on_submit():
        print("The slot to cancel is: ", lesson_to_cancel)
        if current_user.role=="Student":
            user2_id = lesson_to_cancel.tutor_id
        else:
            user2_id = lesson_to_cancel.student_id

        user2_username = User.query.filter_by(id=user2_id).first().username
        cancel_slot(lesson_to_cancel)

        lesson_to_cancel = None

        send_scheduling_emails("cancellation", 1, user2_username, form)

        flash('Your lesson has been cancelled.', 'success')
        #remove_booked_slots_from_db(time_to_cancel)
        return redirect(url_for('main.home'))
    return render_template("cancel_booking.html", form=form)


reschedule_request = {}
@scheduling.route('/reschedule', methods=['GET', 'POST'])
def reschedule():
    global reschedule_request

    flash("Click on a new timeslot.", "info")
    if request.method=="POST":

        print(request.get_json())
        passed_variables = request.get_json()['to_pass_to_flask']
        date_text = passed_variables['date_text']
        date_text = date_text.strip().split("\n")
        day = date_text[0].strip()
        start_time = passed_variables['class_start'].strip()
        time_to_reschedule = datetime.strptime(day + " " + start_time, '%d %b %Y %H:%M')

        lesson_to_reschedule = get_slot_to_reschedule(time_to_reschedule)
        print(lesson_to_reschedule)
        tutor_id = lesson_to_reschedule.tutor_id
        tutor = User.query.filter_by(id=tutor_id).first()
        tutor_username = tutor.username
        student_id = lesson_to_reschedule.student_id

        #tutor_username = request.args.get('tutor_username')
        offset = int(request.args.get('offset')) if request.args.get('offset') else 0
        schedule = load_week(sample_schedule, offset, tutor_username)

        reschedule_request["user"] = current_user
        reschedule_request["slot"] = lesson_to_reschedule
        reschedule_request["tutor_id"] = tutor_id
        reschedule_request["tutor_username"] = tutor_username
        reschedule_request["student_id"] = student_id


        return render_template("reschedule.html", title="Reschedule", tutor_username=tutor_username,
                               schedule=schedule,
                               selected=False, offset=offset, lesson_to_reschedule=lesson_to_reschedule)


    tutor_username = reschedule_request.get("tutor_username")
    lesson_to_reschedule = reschedule_request.get("slot")

    # doing this because reschedule request is a global variable and we don't want another user to reschedule the lesson.
    check_reschedule_request_safety(reschedule_request)

    #reschedule_requests.complete_request(current_user)

    offset = int(request.args.get('offset')) if request.args.get('offset') else 0
    schedule = load_week(sample_schedule, offset, tutor_username)

    return render_template("reschedule.html", title="Reschedule", tutor_username=tutor_username,
                           schedule=schedule,
                           selected=False, offset=offset, lesson_to_reschedule=lesson_to_reschedule)

lesson_to_add = None
@scheduling.route('/confirm_reschedule', methods=['GET', 'POST'])
def confirm_reschedule():
    print(reschedule_request.get("user"), current_user)
    print(reschedule_request.get("slot").student_id, current_user.id)

    # doing this because reschedule request is a global variable and we don't want another user to reschedule the lesson.
    check_reschedule_request_safety(reschedule_request)

    form = RescheduleForm()
    global lesson_to_add

    if request.method=="POST":
        if request.get_json():
            # doing this because reschedule request is a global variable and we don't want another user to reschedule the lesson.
            check_reschedule_request_safety(reschedule_request)

            passed_variables = request.get_json()['to_pass_to_flask']
            date_text = passed_variables['date_text']
            date_text = date_text.strip().split("\n")
            #print(date_text[0].strip(), date_text[-2].strip()  )
            # print(date_text)
            day = date_text[0].strip()
            start_time = passed_variables['class_start'].strip()
            #print(day)
            #print(start_time)
            time_to_add = datetime.strptime(day + " " + start_time, '%d %b %Y %H:%M')
            # print(time_to_cancel)
            if current_user.role=="Student":
                lesson_to_add = create_slot(time_to_add, tutor_id=reschedule_request.get("slot").tutor_id, student_id=current_user.id)
            else:
                lesson_to_add = create_slot(time_to_add, tutor_id=current_user.id, student_id = reschedule_request.get("slot").student_id
                                            )
            #print(lesson_to_reschedule)

        #return render_template("cancel_booking.html", form=form)

            #print(lesson_to_add_user_time)
    lesson_to_remove = reschedule_request.get("slot")
    lesson_to_remove_user_time = user_time(lesson_to_remove.date_time,
                                           pytz.timezone(current_user.time_zone))
    # print(lesson_to_remove_user_time)

    lesson_to_add_user_time = lesson_to_add.date_time.astimezone(pytz.timezone(current_user.time_zone))
    #print(datetime.strftime(lesson_to_add_user_time, "%d %B at %H:%M"))
    if form.validate_on_submit():
        # doing this because reschedule request is a global variable and we don't want another user to reschedule the lesson.
        check_reschedule_request_safety(reschedule_request)

        #print("The slot to cancel is: ", lesson_to_reschedule)
        if current_user.role=="Student":
            user2_id = lesson_to_remove.tutor_id
        else:
            user2_id = lesson_to_remove.student_id

        user2_username = User.query.filter_by(id=user2_id).first().username
        cancel_slot(lesson_to_remove, reschedule=True)
        add_slot(lesson_to_add, reschedule=True)
        lesson_to_remove = None


        send_scheduling_emails("reschedule", 1, user2_username, form)

        flash('Your lesson has been rescheduled.', 'success')
        #remove_booked_slots_from_db(time_to_cancel)
        return redirect(url_for('main.home'))
    return render_template("confirm_reschedule.html", form=form, reschedule_slot=reschedule_request.get("slot"), lesson_to_remove_user_time=datetime.strftime(lesson_to_remove_user_time, "%d %B at %H:%M"), lesson_to_add_user_time=datetime.strftime(lesson_to_add_user_time, "%d %B at %H:%M"))


@scheduling.route('/available_slot')
def available_slot():
    return render_template("available_slot.html", testing_var=False)

@scheduling.route('/reschedule_slot')
def reschedule_slot():
    if reschedule_request.get("user") != current_user:
        # doing this because reschedule request is a global variable and we don't want another user to reschedule the lesson.
        abort(500)
    return render_template("reschedule_slot.html")

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

@scheduling.route('/feedback/<lesson_id>')
@login_required
def send_feedback():
    pass