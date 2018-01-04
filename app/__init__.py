from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
#import easygopigo3 as easyGPG
import gopigo

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config.from_object('config')

#init Gopigo
import atexit
atexit.register(gopigo.stop)
#/init

from app import views
