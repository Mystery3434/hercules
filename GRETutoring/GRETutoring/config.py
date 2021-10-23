import os

class Config:
    SECRET_KEY = os.environ.get("SQL_ALCHEMY_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQL_ALCHEMY_DB_URI")
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')


