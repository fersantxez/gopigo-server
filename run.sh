#!/bin/bash

# gopigo-server: a Flask-based REST server to control a GoPiGo Robot
# Author: Fernando Sanchez (fer@groundcontrol.me)

export PYTHON='venv/bin/python'
export VENV_DIR=${PWD}"/venv"
export DB_FILENAME=${PWD}/app.db
export INIT_DB=${PWD}/init_db.py

if [ ! -d "$VENV_DIR" ]; then
	virtualenv $VENV_DIR
fi
#not needed on a virtual environment#
# for other systems
sudo pip install -r requirements.txt
source ${VENV_DIR}/bin/activate
#if DB dos not exist, initialize it
if [ ! -f "${DB_FILENAME}" ]; then
	${INIT_DB}
fi 

#point Flask to the Main app
export FLASK_APP=gopigo-server.py
export FLASK_DEBUG=1
export FLASK_DEBUG=0

#run
${PYTHON} run.py
