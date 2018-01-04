from app import app
from flask import request, make_response, redirect, abort, render_template, url_for, flash
import socket
from datetime import datetime
import app.util as util
from app.forms import FormForwardCms

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
		#ip='127.0.0.1',   #required if/when not running on linux
		ip=util.get_default_iface_name_linux(),
		current_time=datetime.utcnow()
		)

@app.route('/move', methods=['GET', 'POST'])
def move():
	'''
	Render interface for moving around the GoPiGo
	'''
	
	form_forward_cms = FormForwardCms() 

	if form_forward_cms.validate_on_submit():
		dist = form_forward_cms.forward_distance.data #Integer
		print('**DEBUG dist is {}'.format(dist))
		if dist > 0:
			flash('About to MOVE forward {} cms'.format(dist))
			return redirect(url_for('forward', dist=dist))
		return redirect(url_for('move'))

	return render_template('move.html', formFW=form_forward_cms)

#Motor movement
@app.route('/gopigo/motor/forward/<int:dist>', methods=['GET'])
def forward(dist):
	print('**DEBUG: FORWARD {} cms'.format(dist))
	flash('Moving forward {} cms'.format(dist) )
	gopigo.fwd(dist)
	return redirect(url_for('move'))

@app.route('/gopigo/motor/motor_forward', methods=['GET'])
def motor_forward():
	print('**DEBUG: MOTOR_FORWARD')
	flash('Moving forward until stopped' )
	gopigo.fwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/backward', methods=['GET'])
def backward():
	print('**DEBUG: BACKWARD some cms')
	flash('Moving backwards {} cms'.format( 10 ) )
	gopigo.bwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/motor_backward', methods=['GET'])
def motor_backward():
	print('**DEBUG: BACKWARD')
	flash('Moving backward until stopped' )
	gopigo.motor_bwd()
	return redirect(url_for('move'))
	
@app.route('/gopigo/motor/left', methods=['GET'])
def left():
	print('**DEBUG: LEFT')
	flash('Rotating Left (slow)')
	gopigo.left()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/left_rotation', methods=['GET'])
def left_rotation():
	print('**DEBUG: LEFT ROTATION')
	flash('Rotating Left (fast)')
	gopigo.left_rot()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/right', methods=['GET'])
def right():
	print('**DEBUG: RIGHT')
	flash('Rotating Right (slow)')
	gopigo.right()
	return redirect(url_for('move'))
	
@app.route('/gopigo/motor/right_rotation', methods=['GET'])
def right_rotation():
	print('**DEBUG: RIGHT ROTATION')
	flash('Rotating Right (fast)')
	gopigo.right_rot()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/stop', methods=['GET'])
def stop():
	print('**DEBUG: STOP')
	flash('Stopped')
	gopigo.stop()
	return redirect(url_for('move'))

#Error handlers
@app.errorhandler(404) 
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
