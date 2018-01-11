from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_script import Manager

import os
import logging
from logging.handlers import RotatingFileHandler

import gopigo

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'
manager = Manager(app)

app.config.from_object(Config)

#init Gopigo
import atexit
atexit.register(gopigo.stop)

#Initialize Base directory
if not os.path.exists(Config.BASE_DIR):
    os.makedirs(Config.BASE_DIR)
#initialize Video and Audio directory
if not os.path.exists(Config.MEDIA_FOLDER):
    os.makedirs(Config.MEDIA_FOLDER)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models

if __name__ == '__main__':
	handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	#manager.run( ','.join(map(str, Config.APP_RUN_OPTS)))
	manager.run(host="0.0.0.0", threaded=True)