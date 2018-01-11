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
		"port="+PORT
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


	#audio configuration




	
	
	
