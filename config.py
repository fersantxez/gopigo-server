import os

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

	DATABASE_FILE_NAME = "app.db"
	EMPTY_PICTURE= os.path.join(MEDIA_FOLDER, 'dex-advanced.png')

	PORT = "5001"
	#APP RUN OPTIONS
	APP_RUN_OPTS= [
		"threaded=True",
		"host=0.0.0.0",
		"port="+PORT,
		"debug=False"
		]

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

	OAUTH_CREDENTIALS = {
	    'facebook': {
	        'id': '174382259821684',
	        'secret': 'f4f12aa679f5d946db308f2d3bf02149'
	    },
	    'twitter': {
	        'id': '8rqcSmq71bqauxC3opXQNZsjp',
	        'secret': 'nBniFqPRIHz1xUpkjcwgc1WvTqncOWPk6gh3U5HpgLp2g9WjaA'
	    }
	}


	#audio configuration




	
	
	
