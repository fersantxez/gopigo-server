#!/usr/bin/env python

# init_db: create an initial User for admin purposes with a password to be obtained from the user

from config import Config
from gopigoserver import db
from gopigoserver.models import User, Document
from gopigoserver.util import create_document_from_file

import argparse, os
from sys import exit
import logging
logger = logging.getLogger(Config.APP_NAME)
#from logging.handlers import RotatingFileHandler


if __name__ == "__main__":

	#parse command line arguments
	parser = argparse.ArgumentParser(description='Initialize the gopigo-server database and add an initial Superuser with password', \
		usage='init_db.py -u [USERNAME] -p [PASSWORD]'
		)
	parser.add_argument('-u', '--username', help='username to login with', required=False)
	parser.add_argument('-p', '--password', help='password to login with', required=False)
	args = vars(parser.parse_args())

	#check that the database does not exist
	if os.path.exists( os.path.join( os.getcwd(), Config.DATABASE_FILE_NAME )):
		print('**DEBUG: DATABASE EXISTS. EXITING')
		#app.logger.error('Database exists. Exiting')
		exit(1)

	db.create_all()
	#app.logger.info('Database created')


	#if arguments were not passed, ask for them interactively
	username = args.get('username') or input("Please enter username to initialize the App with: ")
	password = args.get('password') or input("Please enter password for user {}: ".format(username))		

	logger.debug('**DEBUG: about to create a Superuser named {} with password {}'.format(username, password))
	#app.logger.info('About to create a Superuser named {} with password {}'.format(args.get('username'), args.get('password')))
	admin_user = User( 
		username=username,
		social_id="fake_social_id",
		email="Admin User",
		about_me="Pre-generated admin user"
		)
	admin_user.set_password(password)

	#Look for user in db
	if User.query.filter_by(username=admin_user.username).first():
		logger.error('**ERROR: USER {} EXISTS. EXITING'.format(admin_user.username))
		#app.logger.error('User {} exists. Exiting'.format(admin_user.username))
		exit(1)

	db.session.add(admin_user)
	#app.logger.info('Added user {}'.format(admin_user.username))
	db.session.commit()

	#create three pictures with the default icon
	for i in range(1,4):
		empty_picture_full_path = os.path.join( Config.MEDIA_DIR, Config.EMPTY_PICTURE )
		document = create_document_from_file( empty_picture_full_path, type="picture", user_id=admin_user.id )
		if document:
			logger.debug("**DEBUG: Created document {} with name {}".format(document.id, document.name))
		else:
			logger.error("**ERROR creating document {}".format(i))





