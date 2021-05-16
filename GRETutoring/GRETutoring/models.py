from datetime import datetime, timezone, timedelta, tzinfo
from GRETutoring import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_student(student_id):
    return Student.query.get(int(student_id))

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') #nullable=False, since they have to have at least the default
    password = db.Column(db.String(60), nullable=False)
    events = db.relationship('Event', backref='student', lazy=True)

    def __repr__(self):
        return f"Student('{self.username}', '{self.email}','{self.image_file})"

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') #nullable=False, since they have to have at least the default
    password = db.Column(db.String(60), nullable=False)
    events = db.relationship('Event', backref='tutor', lazy=True)
    free_slots = db.relationship('FreeSlot', backref='tutor', lazy=True)

    def __repr__(self):
        return f"Tutor('{self.username}', '{self.email}','{self.image_file})"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.date_time}', '{self.student_id}', '{self.tutor_id}')"

class FreeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.date_time}', '{self.tutor_id}')"