import os
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e1cc8053b63ad42898f458e359ce5ccd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # 3 slashes makes it a relative path from current location
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
socketio = SocketIO(app)
migrate=Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] =  os.environ.get('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] =  os.environ.get('EMAIL_PASSWORD')
mail = Mail(app)


from GRETutoring.main.routes import main
from GRETutoring.messaging.routes import messaging
from GRETutoring.transactions.routes import transactions
from GRETutoring.scheduling.routes import scheduling
from GRETutoring.users.routes import users

app.register_blueprint(main)
app.register_blueprint(messaging)
app.register_blueprint(transactions)
app.register_blueprint(scheduling)
app.register_blueprint(users)