import datetime
import json
from run import app
from GRETutoring import db
from GRETutoring.models import User, Event
import pytz

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

current_year = datetime.datetime.utcnow().year
start_date = datetime.date(current_year, 1, 1)
print(start_date)
# next_monday = next_weekday(d, 5) # 0 = Monday, 1=Tuesday, 2=Wednesday...
# print(next_monday)
days_of_week_dict = {
        "Monday": 0,
        "Tuesday" : 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

with open("placeholder_lessons.json") as f:
    data = json.load(f)

with app.app_context():
    for profile in data["data"]:
        tutor = User.query.filter_by(username=profile["tutor"]).first()
        student = User.query.filter_by(username=profile["student"]).first()
        tutor_tz = pytz.timezone(tutor.time_zone)
        for day, timeslots in profile["slots"].items():
            next_day = start_date
            print(day + "s")
            for i in range(1, 52):
                next_day = next_weekday(next_day, days_of_week_dict[day])
                for slot in timeslots:
                    lesson_time = tutor_tz.localize(datetime.datetime(next_day.year, next_day.month, next_day.day, slot, 0))
                    utc_lesson_time = lesson_time.astimezone(pytz.utc)
                    booked_lesson = Event(tutor_id = tutor.id, student_id = student.id, date_time = utc_lesson_time)
                    db.session.add(booked_lesson)
                    db.session.commit()

