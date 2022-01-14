from flask import abort
from GRETutoring import db
from GRETutoring.models import User, Event, FreeSlot
from flask_login import current_user

from datetime import datetime, timedelta
import pytz
from GRETutoring.scheduling.forms import ScheduleForm, CancellationForm

from GRETutoring import mail
import flask_mail
import os

def user_time(t, tz):
    return tz.fromutc(t)


def load_student_schedule(schedule, offset):
    tz = pytz.timezone(current_user.time_zone)
    current_time = datetime.utcnow()
    current_time = user_time(current_time, tz)

    days_to_subtract = current_time.weekday()
    current_time += timedelta(offset)
    start_of_week = current_time - timedelta(days_to_subtract)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    all_classes = Event.query.filter(Event.date_time >= start_of_week.astimezone(pytz.utc),
                                     Event.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                     Event.student_id == current_user.id).all()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if offset % 7 != 0:
        abort(403)

    for day in days_of_week:
        events = schedule[day][1]
        formatted_date = (current_time - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, [])
        days_to_subtract -= 1

    temp = {"data-start": "14:00", "data-end": "15:15",
            "data-content": "event-yoga-1",
            "data-event": "booked-slot", "event-name": "Yoga Level 1"}

    for event in all_classes:

        start_time = user_time(event.date_time, tz)
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, event_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        # print(datetime.utcnow().replace(tzinfo=pytz.utc), start_time.astimezone(pytz.utc))
        if datetime.utcnow().replace(tzinfo=pytz.utc) > start_time.astimezone(pytz.utc):
            event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                          "data-event": "past-slot", "event-name": "Scheduled Lesson"}
        else:
            event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                          "data-event": "booked-slot", "event-name": "Scheduled Lesson"}
        event_list.append(event_dict)
        schedule[start_day] = (formatted_date, event_list)
    return schedule

def load_week(schedule, offset, tutor_username):
    # current_day = datetime.today()
    tz = pytz.timezone(current_user.time_zone)
    current_time = datetime.utcnow()
    current_time = user_time(current_time, tz)

    days_to_subtract = current_time.weekday()
    current_time += timedelta(offset)
    start_of_week = current_time - timedelta(days_to_subtract)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    all_busy_slots = []

    if current_user.role == "Tutor":
        all_classes = Event.query.filter(Event.date_time >= start_of_week.astimezone(pytz.utc),
                                         Event.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                         Event.tutor_id == current_user.id).all()
        all_free_slots = FreeSlot.query.filter(FreeSlot.date_time >= start_of_week.astimezone(pytz.utc),
                                               FreeSlot.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                               FreeSlot.tutor_id == current_user.id).all()

    else:
        tutor = User.query.filter(User.username == tutor_username).first()
        # print(tutor_username)
        # print(tutor)
        if tutor:
            all_classes = Event.query.filter(Event.date_time >= start_of_week.astimezone(pytz.utc),
                                             Event.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                             Event.tutor_id == tutor.id, Event.student_id == current_user.id).all()
            all_free_slots = FreeSlot.query.filter(FreeSlot.date_time >= start_of_week.astimezone(pytz.utc),
                                                   FreeSlot.date_time < (
                                                               start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                                   FreeSlot.tutor_id == tutor.id).all()
            all_busy_slots = Event.query.filter(Event.date_time >= start_of_week.astimezone(pytz.utc),
                                                Event.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                                Event.tutor_id == tutor.id, Event.student_id != current_user.id).all()
        else:
            all_classes = []
            all_free_slots = []

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if offset % 7 != 0:
        abort(403)

    for day in days_of_week:
        events = schedule[day][1]
        formatted_date = (current_time - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, [])
        days_to_subtract -= 1

    temp = {"data-start": "14:00", "data-end": "15:15",
            "data-content": "event-yoga-1",
            "data-event": "booked-slot", "event-name": "Yoga Level 1"}

    for event in all_classes:

        start_time = user_time(event.date_time, tz)
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, event_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        #print(datetime.utcnow().replace(tzinfo=pytz.utc), start_time.astimezone(pytz.utc))
        if datetime.utcnow().replace(tzinfo=pytz.utc) > start_time.astimezone(pytz.utc):
            event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                          "data-event": "past-slot", "event-name": "Scheduled Lesson"}
        else:
            event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                          "data-event": "booked-slot", "event-name": "Scheduled Lesson"}
        event_list.append(event_dict)
        schedule[start_day] = (formatted_date, event_list)

    for busy_slot in all_busy_slots:
        start_time = user_time(busy_slot.date_time, tz)
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, busy_slot_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        if datetime.utcnow().replace(tzinfo=pytz.utc) > start_time.astimezone(pytz.utc):
            busy_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                              "data-event": "past-slot", "event-name": "Tutor Busy"}
        else:
            busy_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                              "data-event": "busy-slot", "event-name": "Tutor Busy"}

        busy_slot_list.append(busy_slot_dict)
        schedule[start_day] = (formatted_date, busy_slot_list)

    for free_slot in all_free_slots:

        start_time = user_time(free_slot.date_time, tz)
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, free_slot_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        #print(current_time, start_time)
        if datetime.utcnow().replace(tzinfo=pytz.utc) > start_time.astimezone(pytz.utc):
            free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min,
                              "data-content": "event-yoga-1",
                              "data-event": "past-slot", "event-name": "Free Slot"}

        else:
            if current_user.role == "Tutor":
                free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min,
                                  "data-content": "event-yoga-1",
                                  "data-event": "tutor-available-slot", "event-name": "Free Slot"}
            else:
                free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min,
                                  "data-content": "event-yoga-1",
                                  "data-event": "free-slot", "event-name": "Free Slot"}

        free_slot_list.append(free_slot_dict)
        schedule[start_day] = (formatted_date, free_slot_list)

    print(schedule)

    return schedule


def load_week_free_slots(schedule, offset):
    tz = pytz.timezone(current_user.time_zone)
    current_day = datetime.utcnow()
    current_day = user_time(current_day, tz)
    days_to_subtract = current_day.weekday()
    current_day += timedelta(offset)
    start_of_week = current_day - timedelta(days_to_subtract)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    if current_user.role == "Tutor":
        all_classes = Event.query.filter(Event.date_time >= start_of_week.astimezone(pytz.utc),
                                         Event.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                         Event.tutor_id == current_user.id).all()
        all_free_slots = FreeSlot.query.filter(FreeSlot.date_time >= start_of_week.astimezone(pytz.utc),
                                               FreeSlot.date_time < (start_of_week.astimezone(pytz.utc) + timedelta(7)),
                                               FreeSlot.tutor_id == current_user.id).all()

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

    all_start_times = {day: set() for day in days_of_week}

    for event in all_classes:
        start_time = user_time(event.date_time, tz)
        week_day = start_time.weekday()
        start_day = days_of_week[week_day]
        formatted_date, event_list = schedule[start_day]
        start_hour_min = datetime.strftime(start_time, "%H:%M")
        all_start_times[start_day].add(start_hour_min)
        end_hour_min = datetime.strftime(start_time + timedelta(hours=1), "%H:%M")
        end_hour_min = "24:00" if end_hour_min == "00:00" else end_hour_min
        event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                      "data-event": "booked-slot", "event-name": "Scheduled Lesson"}
        event_list.append(event_dict)
        schedule[start_day] = (formatted_date, event_list)

    for free_slot in all_free_slots:
        start_time = user_time(free_slot.date_time, tz)
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
                                               "event-name": ""} for i in range(0, 24) if
                                              f"{i}:00" not in all_start_times[day] and f"0{i}:00" not in
                                              all_start_times[day]]
        events = schedule[day][1]
        events = events + schedule_tutor_free_slots_each_day
        formatted_date = (current_day - timedelta(days_to_subtract)).strftime("%d %b %Y")
        schedule[day] = (formatted_date, events)
        days_to_subtract -= 1
    print(schedule)

    return schedule


def push_free_slots_to_db(schedule):
    tz = pytz.timezone(current_user.time_zone)
    the_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_start = datetime.strptime(schedule["updatedSchedule"]["week_start"].strip(), "%d %b %Y")
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    FreeSlot.query.filter(FreeSlot.date_time >= week_start.astimezone(pytz.utc),
                          FreeSlot.date_time < (week_start.astimezone(pytz.utc) + timedelta(7)),
                          FreeSlot.tutor_id == current_user.id).delete()
    db.session.commit()
    for slot in schedule["updatedSchedule"]["selected"]:
        day = slot["day"]
        start = slot["start"]
        end = slot["end"]
        diff = the_days.index(day)
        class_date = week_start + timedelta(diff)
        start_hour, start_minute = start.split(":")
        class_date = class_date.replace(hour=int(start_hour), minute=int(start_minute))
        class_date = tz.localize(class_date)
        class_event = FreeSlot(date_time=class_date.astimezone(pytz.utc), tutor_id=current_user.id)
        print("FREE SLOTS: ", class_event)
        db.session.add(class_event)
        db.session.commit()

    print("Reached here")


def push_booked_slots_to_db(schedule, tutor_username):
    tz = pytz.timezone(current_user.time_zone)
    print("Entered this function successfully!")
    the_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    week_start = datetime.strptime(schedule["updatedSchedule"]["week_start"].strip(), "%d %b %Y")
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    tutor = User.query.filter(User.username == tutor_username).first()
    num_lessons = len(schedule["updatedSchedule"]["selected"])
    current_user.credits -= num_lessons
    db.session.commit()
    # db.session.commit()
    for slot in schedule["updatedSchedule"]["selected"]:
        day = slot["day"]
        start = slot["start"]
        end = slot["end"]
        diff = the_days.index(day)
        class_date = week_start + timedelta(diff)
        start_hour, start_minute = start.split(":")
        class_date = class_date.replace(hour=int(start_hour), minute=int(start_minute))
        class_date = tz.localize(class_date)
        class_event = Event(date_time=class_date.astimezone(pytz.utc), tutor_id=tutor.id, student_id=current_user.id)
        print("BOOKED SLOTS: ", class_event)
        # Delete the free slot before adding the new slot
        FreeSlot.query.filter(FreeSlot.date_time == class_date.astimezone(pytz.utc),
                              FreeSlot.tutor_id == tutor.id).delete()

        db.session.add(class_event)
        db.session.commit()

    print("Reached here")

def get_slot_to_cancel(slot):
    print("Entered this function (remove booked slots from db) successfully!")
    print("The current user is a ", current_user.role)
    tz = pytz.timezone(current_user.time_zone)
    slot = tz.localize(slot)
    slot_in_utc = slot.astimezone(pytz.utc)
    if current_user.role == "Student":
        db_entry = Event.query.filter(Event.date_time == slot_in_utc,
                       Event.student_id == current_user.id).first()
    else:
        db_entry = Event.query.filter(Event.date_time == slot_in_utc,
                                      Event.tutor_id == current_user.id).first()
    print("The slot chosen to cancel is (db): ", db_entry)
    print("The slot chosen to cancel is (raw): ", slot)
    print("The slot chosen to cancel is (UTC): ", slot_in_utc)
    return db_entry

def cancel_slot(slot):
    free_slot = FreeSlot(date_time=slot.date_time, tutor_id=slot.tutor_id)
    print("FREE SLOTS: ", free_slot)
    db.session.delete(slot)
    db.session.commit()
    student_id = slot.student_id
    student = User.query.filter_by(id=student_id).first()
    student.credits += 1
    db.session.commit()
    db.session.add(free_slot)
    db.session.commit()


def send_scheduling_emails(type, num_lessons, user2_username, form = None):
    # User 1 is the user who initiated the request. If they are a student, then user 2 is the tutor and vice-versa.
    MY_EMAIL = os.environ.get('EMAIL_USERNAME')
    user1_email = current_user.email
    user2_email = User.query.filter_by(username=user2_username).first().email

    verb = {"booking": "booked",
            "cancellation": "cancelled"}

    message_to_user1 = "You have successfully " + verb[type] + " " + str(num_lessons) + " lesson(s) with " + user2_username + \
                         ". Login to your account to view your schedule and to message them.\n\nIf you have any issues or would like to provide feedback on the class, please use the 'Contact Us' page on our website."
    message_to_user2 = current_user.username + " has " + verb[type] + " " + str(num_lessons) + " lesson(s) with you." + \
                       " Login to your account to view your schedule and to message them.\n\nIf you have any issues or would like to provide feedback on the class, please use the 'Contact Us' page on our website."

    if isinstance(form, ScheduleForm):
        special_requests = form.special_requests.data
        verbal = form.verbal.data
        quant = form.quant.data
        awa = form.awa.data
        focus = ""
        if verbal or quant or awa:
            if verbal:
                focus += "\nVerbal Reasoning"
            if quant:
                focus += "\nQuantitative Reasoning"
            if awa:
                focus += "\nAnalytical Writing"
            message_to_user2 += "\n\nThey would like to focus on: " + focus
        if special_requests:
            message_to_user2 += "\n\nTheir special requests for the lesson are:\n " + special_requests

    if isinstance(form, CancellationForm):
        reasons = form.reasons.data
        message_to_user2 += "\n\nThe reason for the cancellation provided by the user is: \n" + reasons

    message_to_admin = current_user.username + " has " + verb[type] + " " + str(
        num_lessons) + " lessons with " + user2_username + "."

    msg_user1 = flask_mail.Message('Hercules lesson ' + type, sender='noreply@demo.com', recipients=[user1_email],
                                     body=message_to_user1)
    msg_user2 = flask_mail.Message('Hercules lesson ' + type, sender='noreply@demo.com', recipients=[user2_email],
                                   body=message_to_user2)
    msg_admin = flask_mail.Message('Hercules lesson ' + type, sender='noreply@demo.com', recipients=[MY_EMAIL],
                                   body=message_to_admin)
    print(msg_user1)
    mail.send(msg_user1)
    mail.send(msg_user2)
    mail.send(msg_admin)