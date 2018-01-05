import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config (object):
	WTF_CSRF_ENABLED = True
	SECRET_KEY = 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	STREAMING_TMP_DIR='/tmp/stream'
	MJPG_LD_LIBRARY_PATH='/opt/mjpg-streamer'
	MJPG_BIN='/opt/mjpg-streamer/mjpg_streamer'
	MPJG_OPTS='-i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -p 9000 -w /opt/mjpg-streamer/www" > /dev/null 2>&1&'
