from flask import Blueprint

api = Blueprint('api', __name__)

from gopigoserver.api_1_0 import errors, authentication  #base, move, servo, motor, camera
