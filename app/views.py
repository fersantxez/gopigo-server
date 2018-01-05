from app import app
from flask import request, make_response, redirect, abort, render_template, url_for, flash
import socket
from datetime import datetime
import app.util as util
from app.forms import FormLogin, FormRegistration, FormForwardCms

from flask_login import login_required, current_user, login_user, logout_user
from app.models import User
from werkzeug.urls import url_parse

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = FormLogin()
    if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = FormRegistration()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Added user {} with email {}!'.format(username, email))
        return redirect(url_for('index'))
    return render_template('register.html', title='Add User', form=form)

@app.route('/move', methods=['GET', 'POST'])
@login_required
def move():
	'''
	Render interface for moving around the GoPiGo
	'''
	
	form_forward_cms = FormForwardCms() 

	if form_forward_cms.validate_on_submit():
		dist = form_forward_cms.forward_distance.data #Integer
		if dist > 0:
			flash('About to MOVE forward {} cms'.format(dist))
			return redirect(url_for('forward', dist=dist))
		return redirect(url_for('move'))

	return render_template('move.html', formFW=form_forward_cms)

#Motor movement
@app.route('/gopigo/motor/forward/<int:dist>', methods=['GET'])
@login_required
def forward(dist):
	print('**DEBUG: FORWARD {} cms'.format(dist))
	flash('Moving forward {} cms'.format(dist) )
	gopigo.fwd(dist)
	return redirect(url_for('move'))

@app.route('/gopigo/motor/motor_forward', methods=['GET'])
@login_required
def motor_forward():
	print('**DEBUG: MOTOR_FORWARD')
	flash('Moving forward until stopped' )
	gopigo.fwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/backward', methods=['GET'])
@login_required
def backward():
	print('**DEBUG: BACKWARD some cms')
	flash('Moving backwards {} cms'.format( 10 ) )
	gopigo.bwd()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/motor_backward', methods=['GET'])
@login_required
def motor_backward():
	print('**DEBUG: BACKWARD')
	flash('Moving backward until stopped' )
	gopigo.motor_bwd()
	return redirect(url_for('move'))
	
@app.route('/gopigo/motor/left', methods=['GET'])
@login_required
def left():
	print('**DEBUG: LEFT')
	flash('Rotating Left (slow)')
	gopigo.left()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/left_rotation', methods=['GET'])
@login_required
def left_rotation():
	print('**DEBUG: LEFT ROTATION')
	flash('Rotating Left (fast)')
	gopigo.left_rot()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/right', methods=['GET'])
@login_required
def right():
	print('**DEBUG: RIGHT')
	flash('Rotating Right (slow)')
	gopigo.right()
	return redirect(url_for('move'))
	
@app.route('/gopigo/motor/right_rotation', methods=['GET'])
@login_required
def right_rotation():
	print('**DEBUG: RIGHT ROTATION')
	flash('Rotating Right (fast)')
	gopigo.right_rot()
	return redirect(url_for('move'))

@app.route('/gopigo/motor/stop', methods=['GET'])
@login_required
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
