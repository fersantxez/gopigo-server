from app import app, db
from app.forms import FormLogin, FormRegistration, FormForwardCms, FormBackwardCms, \
	FormLeftTurnDegrees, FormRightTurnDegrees, FormPic
from app.models import User, Document
import app.util as util
from config import Config
from camera import Camera

from flask import request, make_response, redirect, abort, render_template, url_for, \
	flash, session, send_from_directory, Response
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse

from datetime import datetime
from socket import gethostname
import os
import random #random pics

import gopigo

#Web UI
@app.route('/')
@app.route('/index')
def index():
	'''
	Homepage
	'''
	return render_template('index.html',
		hostname=gethostname(),
		#ip='127.0.0.1',   #required if/when not running on linux
		ip=util.get_default_iface_name_linux(),
		current_time=datetime.utcnow()
		)

@app.route('/<path:filename>')
def send_file(filename):
#serve static files
#if it doesn't exist on MEDIA, search in DB and send_or_404
	file_location = os.path.join(Config.MEDIA_FOLDER,filename)
	if not os.path.exists(file_location):
	#find "filename" in the Database
		document = Document.query.filter_by(name=filename).first()
		#document = get_object_or_404(Document, Document.name == filename)
		#find in database and write body to STATIC directory
		if document:
			#if file doesnt exist, get it from DB (picture just taken not deleted yet)
			try:
				file = open(file_location, 'wb')
				file.write(document.body)
				file.close
			except:
				print('**DEBUG: Error opening file for writing')
				flash('ERROR retrieving document {}'.format(filename), 'error')
				raise IOError
				abort(404)
		else:
			flash('Document {} NOT FOUND'.format(filename), 'error')
			abort(404)
	#return or 404
	return send_from_directory(Config.MEDIA_FOLDER,filename)

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
	
	form_fwd = FormForwardCms()
	form_bwd = FormBackwardCms()
	form_lt = FormLeftTurnDegrees()
	form_rt = FormRightTurnDegrees()

	if form_fwd.validate_on_submit():
		dist = form_fwd.forward_distance.data #Integer
		if dist > 0:
			flash('About to MOVE forward {} cms'.format(dist))
			return redirect(url_for('forward', dist=dist))
		return redirect(url_for('move'))

	if form_bwd.validate_on_submit():
		dist = form_bwd.backward_distance.data
		if dist > 0:
			flash('About to MOVE backward {} cms'.format(dist))
			return redirect(url_for('backward', dist=dist))
		return redirect(url_for('move'))

	if form_lt.validate_on_submit():
		degrees = form_lt.lturn_degrees.data
		if degrees > 0:
			flash('About to TURN left {} degrees'.format(degrees))
			return redirect(url_for('left_turn', degrees=degrees))
		return redirect(url_for('move'))

	if form_rt.validate_on_submit():
		degrees = form_rt.rturn_degrees.data
		if degrees > 0:
			flash('About to TURN right {} degrees'.format(degrees))
			return redirect(url_for('right_turn', degrees=degrees))
		return redirect(url_for('move'))

	return render_template('move.html', \
		formFW=form_fwd, formBW=form_bwd, formLT=form_lt, formRT=form_rt)

#Motor movement
@app.route('/motor/forward/<int:dist>', methods=['GET'])
@login_required
def forward(dist):
	print('**DEBUG: FORWARD {} cms'.format(dist))
	flash('Moving forward {} cms'.format(dist) )
	gopigo.fwd(dist)
	return redirect(url_for('move'))

@app.route('/motor/motor_forward', methods=['GET'])
@login_required
def motor_forward():
	print('**DEBUG: MOTOR_FORWARD')
	flash('Moving forward until stopped' )
	gopigo.fwd()
	return redirect(url_for('move'))

@app.route('/motor/backward/<int:dist>', methods=['GET'])
@login_required
def backward(dist):
	print('**DEBUG: BACKWARD {} cms'.format(dist))
	flash('Moving backward {} cms'.format(dist))
	gopigo.bwd(dist)
	return redirect(url_for('move'))

@app.route('/motor/motor_backward', methods=['GET'])
@login_required
def motor_backward():
	print('**DEBUG: BACKWARD')
	flash('Moving backward until stopped' )
	gopigo.motor_bwd()
	return redirect(url_for('move'))
	
@app.route('/motor/left', methods=['GET'])
@login_required
def left():
	print('**DEBUG: LEFT')
	flash('Rotating Left (slow)')
	gopigo.left()
	return redirect(url_for('move'))

@app.route('/motor/left_rotation', methods=['GET'])
@login_required
def left_rotation():
	print('**DEBUG: LEFT ROTATION')
	flash('Rotating Left (fast)')
	gopigo.left_rot()
	return redirect(url_for('move'))

@app.route('/motor/left_turn/<int:degrees>', methods=['GET'])
@login_required
def left_turn(degrees):
	print('**DEBUG: TURN LEFT {} degrees'.format(degrees))
	flash('Rotating Left {} degrees'.format(degrees))
	gopigo.turn_left(degrees)
	return redirect(url_for('move'))

@app.route('/motor/right', methods=['GET'])
@login_required
def right():
	print('**DEBUG: RIGHT')
	flash('Rotating Right (slow)')
	gopigo.right()
	return redirect(url_for('move'))
	
@app.route('/motor/right_rotation', methods=['GET'])
@login_required
def right_rotation():
	print('**DEBUG: RIGHT ROTATION')
	flash('Rotating Right (fast)')
	gopigo.right_rot()
	return redirect(url_for('move'))

@app.route('/motor/right_turn/<int:degrees>', methods=['GET'])
@login_required
def right_turn(degrees):
	print('**DEBUG: TURN RIGHT {} degrees'.format(degrees))
	flash('Rotating Right {} degrees'.format(degrees))
	gopigo.turn_right(degrees)
	return redirect(url_for('move'))
	
@app.route('/motor/stop', methods=['GET'])
@login_required
def stop():
	print('**DEBUG: STOP')
	flash('Stopped')
	gopigo.stop()
	return redirect(url_for('move'))

@app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
	'''
	Render interface for accesing video/camera with the GoPiGo.
	A live cam with a button that allows to take a picture.
	TODO: allow to record video.
	'''

	form_pic = FormPic()
	picture2 = None
	picture3 = None

	if form_pic.validate_on_submit():
		#stop streaming from the camera to make it available for pictures

		#take a picture and save it to disk
		#return full dictionary with pic and metadata according to Model
		#document = util.take_photo() #this is for camera only without streaming
		document = util.take_photo_from_last_frame(Camera())
		#set current user
		document.user_id=current_user.id
		#upload the body from location(file). Roll back the entire session if failure.
		util.put_document_from_file(document)
		flash( "Picture taken and stored! {}".format(document.name))

		#delete previous "last picture" file from disk (its stored in DB)
		try:
			last_pic_location = os.path.join(Config.MEDIA_FOLDER, session.get('last_picture'))
			if last_pic_location:
				os.remove(last_pic_location)
		except:
			print('**ERROR: Unable to delete last picture')
		#picture just taken is now the last picture
		last_pic_file=document.name
		session['last_picture'] = document.name
		return redirect(url_for('video', formPic=form_pic, last_picture=document.name))

	#TODO:check whether the camera is present and the streaming SW is ready
		#otherwise show processing message and install it if possible
		#if success continue, otherwise redirect to index

	#get two random picture names from the DB for the frame
	rand2 = random.randrange(0, db.session.query(Document).count()) 
	picture2 = Document.query.get(rand2)
	#picture2 = get_object_or_404(Document, Document.id==rand2)
	rand3 = random.randrange(0, db.session.query(Document).count()) 
	#picture3 = get_object_or_404(Document, Document.id==rand3)
	picture3 = Document.query.get(rand3)

	#Start streaming from the camera from the template including three thumbnails
	return render_template('video.html', formPic=form_pic, 
		last_picture=session.get('last_picture'),
		picture2=picture2.name,
		picture3=picture3.name)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(util.yield_video_frames(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#Error handlers
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
