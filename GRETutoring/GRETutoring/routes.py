from flask import render_template, url_for, flash, redirect, request, abort, session
from GRETutoring import app, db, bcrypt, socketio, mail
from GRETutoring.forms import RegistrationForm, ContactUsForm, LoginForm, ScheduleForm, CancellationForm, TutorRegistrationForm, UpdateAccountForm, ReviewForm, RequestResetForm, ResetPasswordForm
from GRETutoring.models import User, Event, FreeSlot, Message, Review
from flask_login import login_user, current_user, logout_user
from flask_login import login_required
from flask_socketio import send, join_room, leave_room, rooms, emit
import secrets
import os
from PIL import Image
from datetime import datetime, timedelta
import calendar
import json
import flask_mail











