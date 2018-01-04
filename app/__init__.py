from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import easygopigo3 as easyGPG

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config.from_object('config')

gopigo = easyGPG.EasyGoPiGo3()

from app import views