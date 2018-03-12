#!venv/bin/python
'''
Main flask routes/actions
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

from werkzeug.urls import url_parse
from datetime import datetime
from socket import gethostname
import os
from time import sleep
from flask import request, make_response, redirect, abort, render_template, url_for, \
    flash, session, send_from_directory, Response, g
from flask_login import login_required, current_user, login_user, logout_user, UserMixin, LoginManager

from gopigoserver.camera import Camera
from gopigoserver import app, db, login
from gopigoserver.forms import FormLogin, FormRegistration, FormForwardCms, FormBackwardCms, \
    FormLeftTurnDegrees, FormRightTurnDegrees, FormPic, FormSettings, FormEdit, FormServo, FormDistance, \
    FormListBuckets, FormVision, FormRecordAudio
from gopigoserver.models import User, Document
import gopigoserver.util as util
import gopigoserver.audio as audio
from gopigoserver.oauth import OAuthSignIn, FacebookSignIn, TwitterSignIn
import gopigoserver.gcp as gcp
import gopigoserver.gopigo as gopigo

#####################
#  Web UI           #
#####################


@app.route('/')
@app.route('/index')
def index():
    '''
    Homepage 
    '''
    return render_template(
        'index.html',
        hostname=gethostname(),
        #ip='127.0.0.1',   #required if/when not running on linux
        ip=util.get_default_iface_name_linux(),
        current_time=datetime.utcnow())


#####################
#  Login            #
#####################


#Before login, set current user
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()  #update "last seen"
        db.session.add(
            g.user)  #add user to DB. FIXME: are we adding empty users?
        db.session.commit()


#Login Manager
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = FormLogin()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            logger.error('Invalid username or password')
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


#Logout from app
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#####################
#  OAuth            #
#####################


#authorize with Oauth through .oauth's OAuthSignIn
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


#callback from OAuth provider
@app.route('/callback/<provider>')
def oauth_callback(provider):
    error = None
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        logger.error('Authentication failed.')
        flash('Authentication failed.', 'error')
        return redirect(url_for('index'))
    user = User.query.filter_by(
        email=email).first()  #find the user by email in dB
    if not user:
        logger.debug('User NOT found in the database')
        flash(
            'User {} not found. Contact your administrator to get it registered'.
            format(email), 'error')
        #this below creates the user if it's not in the dB yet
        #user = User(social_id=social_id, username=username, email=email)
        #db.session.add(user)
        #db.session.commit()
        #login_user(user, True)
        return redirect(url_for('login'))
    else:
        logger.debug('User FOUND in the database as {}'.format(user))
        #update user
        user.social_id = social_id
        user.username = username
        db.session.commit()
        login_user(user, True)
        return redirect(url_for('index'))


#####################
#  User Mgmt        #
#####################


#profile pages
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username, 'error')
        return redirect(url_for('index'))
    documents = [
        #TODO: generate a few documents for the profile page
    ]
    return render_template('user.html', user=user, documents=documents)


#edit profile page
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = FormEdit()
    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.', 'message')
        return redirect(url_for('edit'))
    else:
        form.username.data = g.user.username
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


#serve static files
@app.route('/<path:filename>')
def send_file(filename):
    '''
    Serve a file by the name. Searches for the location in the dB, downloads it to disk and returns it
    '''
    logger.debug('REQUESTED DOCUMENT: {}'.format(filename))
    #if it doesn't exist on MEDIA, search in DB -> GCS and send_or_404
    file_location = os.path.join(Config.MEDIA_DIR, filename)
    if not os.path.exists(file_location):
        #find "filename" in the Database and write to MEDIA dir if it exists
        document = Document.query.filter_by(name=filename).first()
        if document:
            #if file doesnt exist, get it from GCS
            logger.debug('FOUND DOCUMENT in DB: {}'.format(document))
            try:
                logger.debug('opening file_location for DOCUMENT: {}'.format(
                    file_location))
                file = open(file_location, 'wb')
                gcp.read_file_from_bucket(filename, file)
                logger.debug('Downloaded document from GCS to: {}'.format(
                    file_location))
                file.close()
            except Exception as exc:
                logger.error('ERROR opening file for writing {}: {}'.format(
                    file_location, str(exc)))
                flash('ERROR retrieving document {}'.format(filename), 'error')
                raise IOError
                abort(404)
        else:
            flash('Document {} NOT FOUND'.format(filename), 'error')
            abort(404)

    return send_from_directory(Config.MEDIA_DIR, filename)


#Register a new user in system/db
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = FormRegistration()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Added user {} with email {}!'.format(user.username, user.email),
              'message')
        return redirect(url_for('index'))
    return render_template('register.html', title='Add User', form=form)


#####################
#  Movement         #
#####################


#Move the GoPiGo around
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
        dist = form_fwd.forward_distance.data  #Integer
        if dist > 0:
            return redirect(url_for('forward', dist=dist))
        return redirect(url_for('move'))

    if form_bwd.validate_on_submit():
        dist = form_bwd.backward_distance.data
        if dist > 0:
            return redirect(url_for('backward', dist=dist))
        return redirect(url_for('move'))

    if form_lt.validate_on_submit():
        degrees = form_lt.lturn_degrees.data
        if degrees > 0:
            return redirect(url_for('left_turn', degrees=degrees))
        return redirect(url_for('move'))

    if form_rt.validate_on_submit():
        degrees = form_rt.rturn_degrees.data
        if degrees > 0:
            return redirect(url_for('right_turn', degrees=degrees))
        return redirect(url_for('move'))

    return render_template('move.html', \
        formFW=form_fwd, formBW=form_bwd, formLT=form_lt, formRT=form_rt)


#Motor movement
@app.route('/motor/forward/<int:dist>', methods=['GET'])
@login_required
def forward(dist):
    logger.debug('FORWARD {} cms'.format(dist))
    flash('Moving forward {} cms'.format(dist), 'message')
    gopigo.fwd(dist)
    return redirect(url_for('move'))


@app.route('/motor/motor_forward', methods=['GET'])
@login_required
def motor_forward():
    logger.debug('MOTOR_FORWARD')
    flash('Moving forward until stopped', 'message')
    gopigo.fwd()
    return redirect(url_for('move'))


@app.route('/motor/backward/<int:dist>', methods=['GET'])
@login_required
def backward(dist):
    logger.debug('BACKWARD {} cms'.format(dist))
    flash('Moving backward {} cms'.format(dist), 'message')
    gopigo.bwd(dist)
    return redirect(url_for('move'))


@app.route('/motor/motor_backward', methods=['GET'])
@login_required
def motor_backward():
    logger.debug('BACKWARD')
    flash('Moving backward until stopped', 'message')
    gopigo.motor_bwd()
    return redirect(url_for('move'))


@app.route('/motor/left', methods=['GET'])
@login_required
def left():
    logger.debug('LEFT')
    flash('Rotating Left (slow)')
    gopigo.left()
    return redirect(url_for('move'))


@app.route('/motor/left_rotation', methods=['GET'])
@login_required
def left_rotation():
    logger.debug('LEFT ROTATION')
    flash('Rotating Left (fast)', 'message')
    gopigo.left_rot()
    return redirect(url_for('move'))


@app.route('/motor/left_turn/<int:degrees>', methods=['GET'])
@login_required
def left_turn(degrees):
    logger.debug('TURN LEFT {} degrees'.format(degrees))
    flash('Rotating Left {} degrees'.format(degrees), 'message')
    gopigo.turn_left(degrees)
    return redirect(url_for('move'))


@app.route('/motor/right', methods=['GET'])
@login_required
def right():
    logger.debug('RIGHT')
    flash('Rotating Right (slow)', 'message')
    gopigo.right()
    return redirect(url_for('move'))


@app.route('/motor/right_rotation', methods=['GET'])
@login_required
def right_rotation():
    logger.debug('RIGHT ROTATION')
    flash('Rotating Right (fast)', 'message')
    gopigo.right_rot()
    return redirect(url_for('move'))


@app.route('/motor/right_turn/<int:degrees>', methods=['GET'])
@login_required
def right_turn(degrees):
    logger.debug('TURN RIGHT {} degrees'.format(degrees))
    flash('Rotating Right {} degrees'.format(degrees), 'message')
    gopigo.turn_right(degrees)
    return redirect(url_for('move'))


@app.route('/motor/stop', methods=['GET'])
@login_required
def stop():
    logger.debug('STOP')
    flash('Stopped', 'message')
    gopigo.stop()
    return redirect(url_for('move'))


#####################
#  Video            #
#####################


#turn on the camera, take pictures, show previous pictures taken
@app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
    '''
    Render interface for accesing video/camera with the GoPiGo.
    A live cam with a button that allows to take a picture.
    TODO: allow to record video.
    '''
    form_pic = FormPic()

    if form_pic.validate_on_submit():
        #stop streaming from the camera to make it available for pictures
        #take a picture and save it to disk
        #return full dictionary with pic and metadata according to Model
        #document = util.take_photo() #this is for camera only without streaming
        pic_location = util.take_photo_from_last_frame(Camera())
        #Create the document in the database from the file
        document = util.create_document_from_file(pic_location, "picture",
                                                  current_user.id)
        if document:
            flash("Picture taken and stored! {}".format(document.name),
                  'message')
            return redirect(
                url_for('video', formPic=form_pic, last_picture=document.name))
        else:
            flash("Error taking picture!", 'error')

    recent_pictures = [
    ]  #Holds the pictures that will be shown in the menu as "recent pictures"
    for i, blob in enumerate(reversed(list(
            gcp.blobs_in_bucket()))):  #return the most recent docs
        filename = blob.name
        recent_pictures.append(filename)
        logger.debug('appended number {}: {}'.format(i, filename))
        if i > 3:
            break
    #if there are not enough pics in bucket, fill with EMPTY_PICTURE
    while len(recent_pictures) < 3:
        recent_pictures.append(Config.EMPTY_PICTURE)
        logger.debug('appending an empty picture: {}'.format(
            Config.EMPTY_PICTURE))

    #TODO:check whether the camera is present and the streaming SW is ready
    #otherwise show processing message and install it if possible
    #if success continue, otherwise redirect to index

    #Start streaming from the camera from the template including three thumbnails
    return render_template(
        'video.html',
        formPic=form_pic,
        picture1=recent_pictures[0],
        picture2=recent_pictures[1],
        picture3=recent_pictures[2])


#serve the video feed -- this will embedded in other pages
@app.route('/video_feed')
@login_required
def video_feed():
    '''
    Video streaming route. Put this in the src attribute of an img tag.
    '''
    return Response(
        util.yield_video_frames(Camera()),
        mimetype='multipart/x-mixed-replace; boundary=frame')


#####################
#  Settings         #
#####################


#settings page
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    '''
    Display the change settings page"""
    '''

    form = FormSettings()

    if form.validate_on_submit():

        #update app configuration
        new_resolution = Config.CAMERA_RES_LIST[int(form.camera_res.data)
                                                - 1][1]
        #-1: form starts in 1, array in 0
        Config.CAMERA_RES = new_resolution
        Config.CAMERA_SHARPNESS = form.camera_sharpness.data
        flash('Settings updated. New res: {} New sharp: {}'.format(\
            Config.CAMERA_RES, Config.CAMERA_SHARPNESS, 'message'))
        pass

    return render_template('settings.html', title='Settings', form=form)


#####################
#  Servo            #
#####################


#Servo and distance detection
@app.route('/servo', methods=['GET', 'POST'])
@login_required
def servo():
    '''
    Display the Servo page
    '''
    form = FormServo()
    if form.validate_on_submit():
        position = form.position.data
        logger.debug('form.position is {}'.format(position))
        gopigo.servo(position)
        logger.info(
            'Head position changed. Now "looking" towards {}'.format(position))
        flash(
            'Head position changed. Now "looking" towards {}'.format(position),
            'message')
        gopigo.disable_servo()  #avoid jittering
    return render_template('servo.html', form=form)


#####################
#  Distance IR      #
#####################


#Measure the distance
@app.route('/distance', methods=['GET', 'POST'])
@login_required
def distance():
    '''
    Display the Distance page
    '''
    form = FormDistance()
    if form.validate_on_submit():
        distance = gopigo.us_dist(Config.PIN_NUMBER_SERVO)
        logger.debug('I can see an object at {} cms from me'.format(distance))
        flash('I can see an object at {} cms from me'.format(distance),
              'message')
    return render_template('distance.html', form=form)


#####################
#  Vision API       #
#####################


#Vision API
@app.route('/vision/<picture>', methods=['GET', 'POST'])
@login_required
def vision(picture=Config.EMPTY_PICTURE):
    '''
    Display the GCP vision API page
    '''
    formVision = FormVision()
    logger.debug('Called /vision with picture: {}'.format(picture))
    if formVision.validate_on_submit():
        feature = Config.VISION_API_FEATURES_LIST[int(formVision.feature.data)
                                                  - 1][1]
        logger.debug(
            'Calling GCP vision with picture: {} and feature: {}'.format(
                picture, feature))
        unpack_function_name = Config.VISION_API_UNPACK_FUNCTIONS[feature]
        logger.debug(
            'UNPACK function name is: {}'.format(unpack_function_name))
        api_replies_list = gcp.vision_api(picture, feature,
                                          unpack_function_name)
        if not api_replies_list:
            logger.info('API response empty')
            flash('Nothing found', 'error')
        for i, response in enumerate(api_replies_list):
            logger.info('API response element {}: {}'.format(i, response))
            flash('Thing {} Ive found is: {}'.format(i + 1, response),
                  'message')
            #audio.say(response) #optionally say out loud what you saw
    return render_template('vision.html', form=formVision, picture=picture)


#####################
#  Speech API       #
#####################


#Voice recognition and Chatbot
@login_required
@app.route('/voice/<topic>', methods=['GET', 'POST'])
def voice(topic='human resources'):
    '''
    Display the Chatbot page
    FIXME: WIP / broken
    '''
    form = FormRecordAudio()
    if form.validate_on_submit():
        #record and play the audio
        if form.start_recording.data:
            #start recording
            filename = util.filename_from_date('audio', 'wav')
            filepath = os.path.join(Config.MEDIA_DIR, filename)
            flash('Audio recording started', 'message')
            logger.debug('Audio recording started to {}'.format(filepath))
            audio.listen(filepath, 2)  #listen for 5 seconds
            #wait until the recording is finished
            sleep(3)
            flash('Audio recording finished, playing recording', 'message')
            logger.debug('Audio recording finished. Playing')
            audio.play_wave(filepath)
            logger.debug('PLAY finished, returning to page')
            flash(
                'Audio recording Play finished, thank you for your collaboration',
                'message')
            #os.remove(filename)
        if form.stop_recording.data:
            #do something with the audio
            #for example, read the recording aloud
            flash('AUDIO recording STOP is not supported yet', 'message')
            logger.debug('AUDIO recording STOP is not supported yet')
    return render_template('voice.html', topic=topic, form=form)


#####################
#  Error handlers   #
#####################


#Error handlers - only for 404 and 500, others are API specific
@app.errorhandler(404)
def page_not_found(e):
    #content negotiation for API clients
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@app.errorhandler(500)
def forbidden(message):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({
            'error': 'internal server error. ouch!',
            'message': message
        })
        response.status_code = 500
        return response
    return render_template('500.html'), 500
