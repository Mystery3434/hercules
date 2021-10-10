from datetime import datetime, timezone, timedelta, tzinfo
from GRETutoring import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default = "Student")
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') #nullable=False, since they have to have at least the default
    password = db.Column(db.String(60), nullable=False)
    about = db.Column(db.Text(), nullable=True, default = "Bio")
    skype_id = db.Column(db.String(120), nullable=True, default="")
    hangouts_id = db.Column(db.String(120), nullable=True, default="")
    time_zone = db.Column(db.String(120), nullable=True, default="UTC")
    student_classes = db.relationship('Event', backref='student', lazy=True, foreign_keys='Event.student_id')
    tutor_classes = db.relationship('Event', backref='tutor', lazy=True, foreign_keys='Event.tutor_id')
    tutor_free_slots = db.relationship('FreeSlot', backref='tutor', lazy=True)
    sent_messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    received_messages = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')
    reviews_about = db.relationship('Review', backref='tutor', lazy=True, foreign_keys='Review.tutor_id')
    reviews_written = db.relationship('Review', backref='student', lazy=True, foreign_keys='Review.student_id')


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id  = s.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.role}('{self.username}', '{self.email}','{self.image_file})"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Class('{self.date_time}', '{self.student_id}', '{self.tutor_id}')"


class FreeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"FreeSlot('{self.date_time}', '{self.tutor_id}')"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_text = db.Column(db.Text(), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Message('{self.message_text}', '{self.date_time}', '{self.sender_id}', '{self.recipient_id}')"

    def asdict(self):
        return {"id":self.id, "message_text":self.message_text, "date_time":self.date_time, "sender_id":self.sender_id, "recipient_id":self.recipient_id}


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text(), nullable=False)
    review_score = db.Column(db.Float, nullable=True, default=0.0)
    date_time = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Review('{self.review_text}', '{self.date_time}', '{self.student_id}', '{self.tutor_id}')"

    def asdict(self):
        return {"id":self.id, "review_text":self.review_text, "review_score":self.review_score, "date_time":self.date_time, "student_id":self.student_id, "tutor_id":self.tutor_id}

# class Student(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email=db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg') #nullable=False, since they have to have at least the default
#     password = db.Column(db.String(60), nullable=False)
#     events = db.relationship('Event', backref='student', lazy=True)
#
#     def __repr__(self):
#         return f"Student('{self.username}', '{self.email}','{self.image_file})"
#
# class Tutor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email=db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg') #nullable=False, since they have to have at least the default
#     password = db.Column(db.String(60), nullable=False)
#     events = db.relationship('Event', backref='tutor', lazy=True)
#     free_slots = db.relationship('FreeSlot', backref='tutor', lazy=True)
#
#     def __repr__(self):
#         return f"Tutor('{self.username}', '{self.email}','{self.image_file})"
