from app import app
from flask import request, make_response, redirect, abort, render_template, url_for
import socket
from datetime import datetime
import gopigo.I2C_mutex as I2C_mutex
import gopigo.easygopigo3 as easyGPG
import app.util as util
#import app.forms as forms


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
	print('**DEBUG: FORWARD')
	gpg.forward()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/backward', methods=['GET'])
def backward():
	print('**DEBUG: BACKWARD')
	return redirect(url_for('move'))

@app.route('/gopigo/motor/left', methods=['GET'])
def left():
	print('**DEBUG: LEFT')
	return redirect(url_for('move'))

@app.route('/gopigo/motor/right', methods=['GET'])
def right():
	print('**DEBUG: RIGHT')
	return redirect(url_for('move'))

@app.route('/gopigo/motor/stop', methods=['GET'])
def stop():
	print('**DEBUG: STOP')
	return redirect(url_for('move'))

#Error handlers
@app.errorhandler(404) 
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
