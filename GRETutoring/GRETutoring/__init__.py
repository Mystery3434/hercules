
from GRETutoring.config import  Config
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
socketio = SocketIO()
migrate=Migrate()

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from GRETutoring.main.routes import main
    from GRETutoring.messaging.routes import messaging
    from GRETutoring.transactions.routes import transactions
    from GRETutoring.scheduling.routes import scheduling
    from GRETutoring.users.routes import users
    from GRETutoring.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(messaging)
    app.register_blueprint(transactions)
    app.register_blueprint(scheduling)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    return app