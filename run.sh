#!/bin/bash

# gopigo-server: a Flask-based REST server to control a GoPiGo Robot
# Author: Fernando Sanchez (fer@groundcontrol.me)

export VENV_DIR=${PWD}"/venv"

if [ ! -d "$VENV_DIR" ]; then
	virtualenv $VENV_DIR
fi
#not needed on a virtual environment#
# for other systems
source ${VNENV_DIR}/bin/activate
sudo pip install -r requirements.txt


#point Flask to the Main app
export FLASK_APP=gopigo-server.py
#export FLASK_DEBUG=1
export FLASK_DEBUG=0

<<<<<<< HEAD
=======
#not needed on a virtual environment#
# for other systems
# sudo pip install -r requirements.txt
>>>>>>> 4744e6622f0e324f5e329ab2ff38d580fe87fa0f

#run
flask run --with-threads --host='0.0.0.0'
