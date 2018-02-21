from flask import jsonify
from gopigoserver.api_1_0 import api
from gopigoserver.exceptions import ValidationError

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

#Error handlers - start with the @api so they dont overwrite the "main" ones?
#@api.errorhandler(403) 
#def forbidden(message):
#	response = jsonify({'error': 'forbidden', 'message': message}) 
#	response.status_code = 403
#	return response

#redirect all errors to a bad_request with the function name above as argument
@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])

def bad_request(message):
	logger.error('API access: {}'.format(message))
	response = jsonify({'error': 'bad request', 'message': message})
	response.status_code = 400
	return response


def unauthorized(message):
	logger.error('API access: {}'.format(message))
	response = jsonify({'error': 'unauthorized', 'message': message})
	response.status_code = 401
	return response


def forbidden(message):
	logger.error('API access: {}'.format(message))
	response = jsonify({'error': 'forbidden', 'message': message})
	response.status_code = 403
	return response
