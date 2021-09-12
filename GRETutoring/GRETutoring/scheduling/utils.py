from flask import abort
from GRETutoring import app, db
from GRETutoring.models import User, Event, FreeSlot
from flask_login import current_user

from datetime import datetime, timedelta









def load_week(schedule, offset, tutor_username):
    current_day = datetime.today()
    current_time = datetime.now()
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
        print(current_time, start_time)
        if current_time > start_time:
            event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1", "data-event": "past-slot", "event-name":"Scheduled Lesson"}
        else:
            event_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                          "data-event": "booked-slot", "event-name": "Scheduled Lesson"}
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
        if current_time > start_time:
            busy_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                              "data-event": "past-slot", "event-name": "Tutor Busy"}
        else:
            busy_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
                              "data-event": "busy-slot", "event-name": "Tutor Busy"}

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

        if current_time > start_time:
            free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min,
                              "data-content": "event-yoga-1",
                              "data-event": "past-slot", "event-name": "Free Slot"}

        else:
            if current_user.role=="Tutor":
                free_slot_dict = {"data-start": start_hour_min, "data-end": end_hour_min, "data-content": "event-yoga-1",
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
