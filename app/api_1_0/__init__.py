from flask import Blueprint

api = Blueprint('api', __name__)

from . import base, move, servo, motor, camera

def create_app(config_name): 
# ...
from .api_1_0 import api as api_1_0_blueprint 
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0') 
# ...