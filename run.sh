#!/bin/bash

# gopigo-server: a Flask-based REST server to control a GoPiGo Robot
# Author: Fernando Sanchez (fer@groundcontrol.me)

export VENV_DIR=${PWD}"/venv"

if [ ! -d "$VENV_DIR" ]; then
	virtualenv $VENV_DIR
fi
#not needed on a virtual environment#
# for other systems
source ${VENV_DIR}/bin/activate
sudo pip install -r requirements.txt


#point Flask to the Main app
export FLASK_APP=gopigo-server.py
#export FLASK_DEBUG=1
export FLASK_DEBUG=0

#run
flask run --with-threads --host='0.0.0.0'
