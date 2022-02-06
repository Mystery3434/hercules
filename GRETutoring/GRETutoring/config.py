import os, platform, json

if platform.system() == "Windows":
    config = os.environ
else:
    with open('/etc/config.json') as config_file:
        config = json.load(config_file)


class Config:
    SECRET_KEY = config.get("SQL_ALCHEMY_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = config.get("SQL_ALCHEMY_DB_URI")
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config.get('EMAIL_USERNAME')
    MAIL_PASSWORD = config.get('EMAIL_PASSWORD')
    STRIPE_PUBLIC_KEY = config.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = config.get('STRIPE_SECRET_KEY')


