from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_script import Manager

from config import Config

import os
import sys
import datetime
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

#initialize Video and Audio directory - not used if using GCP
if not os.path.exists(Config.MEDIA_FOLDER):
    os.makedirs(Config.MEDIA_FOLDER)

#init GCP application default credentials
logger.debug('GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION is {}'.format(Config.GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION

#initialize app -- TODO: add app blueprint
from app import views, models

#import API blueprint after initializing the app
from .api_1_0 import api as api_1_0_blueprint
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0') 

#init GCP storage bucket - specific for this session
import util
default_ifname =  util.get_default_iface_name_linux()
mac_address = util.get_iface_mac_address(default_ifname)
#bucket_name = "gopigo-server-"+str(datetime.datetime.now()).replace(" ", "").replace(":", "").replace(".", "")
bucket_name = "gopigo-server-"+mac_address.replace(":", "")
import gcp
#find out whether the bucket exists, create otherwise
#if gcp.bucket_exists(bucket_name):
#	logger.info('GCS bucket {} exists, using it'.format(bucket_name))
#	bucket = gcp.get_bucket(bucket_name)
#else:
#	logger.info('GCS bucket {} does not exist, creating it'.format(bucket_name))
#	bucket = gcp.create_bucket(bucket_name)
try:
	bucket = gcp.create_bucket(bucket_name)
	logger.info('GCS bucket {} does not exist, creating it'.format(bucket_name))
except: #google.cloud.exceptions.Conflict:
	logger.info('GCS bucket {} already exists, using it'.format(bucket_name))
Config.bucket_name = bucket.name
logger.debug('Stored bucket {}'.format(Config.bucket_name))

if __name__ == '__main__':
	handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	logger.debug('about to run')
	#manager.run( ','.join(map(str, Config.APP_RUN_OPTS)))
	#manager.run(host="0.0.0.0", threaded=True)
	manager.run(Config.APP_RUN_OPTS)
	logger.debug('running')