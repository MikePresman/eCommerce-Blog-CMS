from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from celery import Celery
import os


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login = LoginManager(app)

mail = Mail(app)

csrf = CSRFProtect(app)

celery = Celery('app', backend='rpc://', broker='pyamqp://guest@localhost//')


#Username : Admin, Password: 1234

#is the stuff below necessary?
@login.user_loader
def load_user(user_id):
    return None

from vms import routes, models
