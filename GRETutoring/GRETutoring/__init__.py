from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e1cc8053b63ad42898f458e359ce5ccd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # 3 slashes makes it a relative path from current location
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
socketio = SocketIO(app)
migrate=Migrate(app, db)

from GRETutoring import routes
