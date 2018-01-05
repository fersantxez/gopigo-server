from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import gopigo

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'

app.config.from_object(Config)

#init Gopigo
import atexit
atexit.register(gopigo.stop)
#/init

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
