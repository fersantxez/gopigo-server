import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class Config (object):
	WTF_CSRF_ENABLED = True
	SECRET_KEY = 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	#Working directories
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	MEDIA_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'media')	#for static content
	#EMPTY_PICTURE= os.path.join(MEDIA_FOLDER, 'dex-advanced.png
	EMPTY_PICTURE='dex-advanced.png'

	DATABASE_FILE_NAME = "app.db"

	PORT = 5000
	
	DEBUG_MODE = True
	
	#APP RUN OPTIONS
	APP_RUN_OPTS = {
		'host':		'0.0.0.0',
		'threaded':	'True',
		'port':		PORT,
		'debug':	DEBUG_MODE
		}

	#logging options
	APP_NAME = 'gopigo-server'
	logger = logging.getLogger(APP_NAME)
	LOGGING_FORMAT = '%(asctime)-15s %(message)s' #'%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
	if DEBUG_MODE:
		LOGGING_LEVEL = logging.DEBUG 
	else:
		LOGGING_LEVEL = logging.INFO

	#storage configuration
	STORAGE_TYPE = "local" #local , gcs , s3

	#video configuration
	CAMERA_RES = "640x480"
	CAMERA_SHARPNESS = 100
	
	#camera resolutions
	CAMERA_RES_LIST=[
	    ("1", "VGA"),
	    ("2", "640x480"),
	    ("3", "1024x768"),
	    ("4", "1280x720"),
	    ("5", "HD")
	    ]

	#TODO: read these from an environment variable
	OAUTH_CREDENTIALS = {
	    'facebook': {
	        'id': '174382259821684',
	        'secret': 'f4f12aa679f5d946db308f2d3bf02149'
	    },
	    'twitter': {
	        'id': '8rqcSmq71bqauxC3opXQNZsjp',
	        'secret': 'nBniFqPRIHz1xUpkjcwgc1WvTqncOWPk6gh3U5HpgLp2g9WjaA'
	    },
	    'google': {
	        'id': '742545609133-3tg386j5flmqbvub28oshb417f6vblui.apps.googleusercontent.com',
	        'secret': 'qaotl6xMdBLTcSAIm5iiYCar'
	    },
	}

	PIN_NUMBER_SERVO = 15 #this is port A1 according to https://github.com/DexterInd/GoPiGo/blob/master/Software/Python/Examples/Ultrasonic_Servo/us_servo_scan.py

	#audio configuration

	#HTTP Authentication configuration
	TOKEN_EXPIRATION = 3600 #seconds

	#GCP app dafault credentials location - Read from environment variable or hardcode by default
	GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION=os.environ.get(
		'GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION',
		"/home/pi/.ssh/gcp-application-default-credentials.json" )		#default value if var not defined
	logger.debug('GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION: {}'.format(GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION))

	bucket_name = "" #to be set on app init

	#Vision API parameters and function associated with each that processes the API response
	VISION_API_FEATURES_LIST=[
		("1", "LABEL_DETECTION"),
		("2", "TEXT_DETECTION"),
		("3", "DOCUMENT_TEXT_DETECTION"),
		("4", "FACE_DETECTION"),
		("5", "LANDMARK_DETECTION"),
		("6", "LOGO_DETECTION"),
		("7", "SAFE_SEARCH_DETECTION"),
		("8", "IMAGE_PROPERTIES")
	    ]

	VISION_API_UNPACK_FUNCTIONS={
	"LABEL_DETECTION": "unpack_label_detection",
	"TEXT_DETECTION": "unpack_text_detection",
	"DOCUMENT_TEXT_DETECTION": "unpack_document_text_detection",
	"FACE_DETECTION": "unpack_face_detection",
	"LANDMARK_DETECTION": "unpack_landmark_detection",
	"LOGO_DETECTION": "unpack_logo_detection",
	"SAFE_SEARCH_DETECTION": "unpack_safe_search_detection",
	"IMAGE_PROPERTIES": "unpack_image_properties"
	}

	#how to describe each feature from the face detection api
	FACE_DETECTION_FEATURES={
	"joy_likelihood":	"joy",
	"sorrow_likelihood":	"sorrow",
	"anger_likelihood":	"anger",
	"surprise_likelihood":	"surprise",
	"headwear_likelihood":	"headwear"
	}

	#when to consider a value as detected
	LIKELIHOOD_NAME = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')
	ACCEPTED_LIKELIHOOD = ("VERY_LIKELY", "LIKELY")   #"POSSIBLE"
	
	
	
