from flask import Blueprint

from flask import render_template, url_for, request
from GRETutoring import db, socketio
from GRETutoring.models import User, Message
from flask_login import current_user
from flask_login import login_required
from flask_socketio import send, join_room, leave_room, emit
from datetime import datetime
import pytz
import json



messaging = Blueprint('messaging', __name__)



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
    #print("Full Data: ", data)
    participants = sorted([source_username, target_username])
    room = user_to_sid[participants[0]] + user_to_sid[participants[1]]

    sender_id = User.query.filter_by(username=source_username).first().id
    recipient_id = User.query.filter_by(username=target_username).first().id

    message = Message(message_text=data["text"], date_time = datetime.utcnow(), sender_id=sender_id, recipient_id=recipient_id)

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
    #print(messages_to_load)

    messages_to_pass = []

    tz = pytz.timezone(current_user.time_zone)

    for message in messages_to_load:
        message_to_pass = message.asdict()
        message_to_pass["sender_username"] = User.query.filter_by(id=message_to_pass["sender_id"]).first().username
        message_to_pass["recipient_username"] = User.query.filter_by(id=message_to_pass["recipient_id"]).first().username
        message_to_pass["date_time"] = tz.fromutc(message_to_pass["date_time"]).strftime("%H:%M")

        messages_to_pass.append(message_to_pass)

    #print(messages_to_pass)
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




@messaging.route('/message')
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
        user_dict["time_zone"] = associated_user.time_zone
        received_messages = Message.query.filter_by(sender_id=associated_user.id, recipient_id=current_user.id).all()
        received_messages += Message.query.filter_by(sender_id=current_user.id, recipient_id=associated_user.id).all()
        received_messages.sort(key=lambda x:x.date_time)
        user_dict["last_received_message"] = "" if not received_messages else received_messages[-1].message_text
        if len(user_dict["last_received_message"]) >= 20:
            user_dict["last_received_message"] = user_dict["last_received_message"][:20] + "..."
        users_list.append(user_dict)
        user_dict = {}



    return render_template("message.html", users = users_list, users_json=json.dumps(users_list))


