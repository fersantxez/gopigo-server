from app import app
from flask import request, make_response, redirect, abort, render_template, url_for
import socket
from datetime import datetime
import app.util as util
#import app.forms as forms

import gopigo


#Web UI
@app.route('/')
@app.route('/index')
def index():
	'''
	Homepage
	'''
	return render_template('index.html', 
		hostname=socket.gethostname(), 
		#ip='127.0.0.1', 
		ip=util.get_default_iface_name_linux(),
		current_time=datetime.utcnow())

@app.route('/move', methods=['GET', 'POST'])
def move():
	'''
	Render interface for moving around the GoPiGo
	'''

	return render_template('move.html')

#Motor movement
@app.route('/gopigo/motor/forward', methods=['GET'])
def forward():
	print('**DEBUG: FORWARD some cms')
	gopigo.fwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/motor_forward', methods=['GET'])
def motor_forward():
	print('**DEBUG: MOTOR_FORWARD')
	gopigo.fwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/backward', methods=['GET'])
def backward():
	print('**DEBUG: BACKWARD some cms')
	gopigo.bwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/motor_backward', methods=['GET'])
def motor_backward():
	print('**DEBUG: BACKWARD some cms')
	gopigo.motor_bwd()
	return redirect(url_for('move'))
	
@app.route('/gopigo/motor/left', methods=['GET'])
def left():
	print('**DEBUG: LEFT')
	gopigo.left()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/left_rotation', methods=['GET'])
def left_rotation():
	print('**DEBUG: LEFT ROTATION')
	gopigo.left_rot()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/right', methods=['GET'])
def right():
	print('**DEBUG: RIGHT')
	gopigo.right()
	return redirect(url_for('move'))
	
@app.route('/gopigo/motor/right_rotation', methods=['GET'])
def right_rotation():
	print('**DEBUG: RIGHT ROTATION')
	gopigo.right_rot()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/stop', methods=['GET'])
def stop():
	print('**DEBUG: STOP')
	gopigo.stop()
	return redirect(url_for('move'))

#Error handlers
@app.errorhandler(404) 
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
