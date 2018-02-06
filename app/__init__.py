from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_script import Manager

from config import Config

import os
import sys
import logging
logger = logging.getLogger(Config.APP_NAME)

import gopigo


#init logger
logging.basicConfig(format=Config.LOGGING_FORMAT)
logger = logging.getLogger(Config.APP_NAME)
logger.setLevel(Config.LOGGING_LEVEL)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(Config.LOGGING_LEVEL)
formatter = logging.Formatter(Config.LOGGING_FORMAT)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('logging initialized')

#create app
#init handlers and flask app
app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
moment = Moment(app)
#init login
login = LoginManager(app)
login.login_view = 'login'
#init app manager/launcher
manager = Manager(app)
#init DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#init HW / Gopigo
import atexit
atexit.register(gopigo.stop)

#init Base directory
if not os.path.exists(Config.BASE_DIR):
    os.makedirs(Config.BASE_DIR)

#initialize Video and Audio directory
if not os.path.exists(Config.MEDIA_FOLDER):
    os.makedirs(Config.MEDIA_FOLDER)

#initialize app -- TODO: add app blueprint
from app import views, models

#import API blueprint after initializing the app
from .api_1_0 import api as api_1_0_blueprint
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0') 

if __name__ == '__main__':
	handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	#manager.run( ','.join(map(str, Config.APP_RUN_OPTS)))
	#manager.run(host="0.0.0.0", threaded=True)
	manager.run(Config.APP_RUN_OPTS)