#!/usr/bin/env python

# init_db: create an initial User for admin purposes with a password to be obtained from the user

from config import Config
from app import db
from app.models import User, Document

import argparse, os
from sys import exit
#import logging
#from logging.handlers import RotatingFileHandler

DATABASE_FILE_NAME = "app.db"

if __name__ == "__main__":

	#parse command line arguments
	parser = argparse.ArgumentParser(description='Initialize the gopigo-server database and add an initial Superuser with password', \
		usage='init_db.py -u [USERNAME] -p [PASSWORD]'
		)
	parser.add_argument('-u', '--username', help='username to login with', required=True)
	parser.add_argument('-p', '--password', help='password to login with', required=True)
	args = vars(parser.parse_args())

	#check that the database does not exist
	if os.path.exists( os.path.join( os.getcwd(),DATABASE_FILE_NAME )):
		print('**DEBUG: DATABASE EXISTS. EXITING')
		#app.logger.error('Database exists. Exiting')
		exit(1)

	db.create_all()
	#app.logger.info('Database created')

	print('**DEBUG: about to create a Superuser named {} with password {}'.format(args.get('username'), args.get('password')))
	#app.logger.info('About to create a Superuser named {} with password {}'.format(args.get('username'), args.get('password')))
	admin_user = User( 
		username=args.get('username'),
		)
	admin_user.set_password(args.get('password'))

	#Look for user in db
	if User.query.filter_by(username=admin_user.username).first():
		print('**DEBUG: USER {} EXISTS. EXITING'.format(admin_user.username))
		#app.logger.error('User {} exists. Exiting'.format(admin_user.username))
		exit(1)

	db.session.add(admin_user)
	#app.logger.info('Added user {}'.format(admin_user.username))

	db.session.commit()



