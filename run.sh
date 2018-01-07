#!/bin/bash

# gopigo-server: a Flask-based REST server to control a GoPiGo Robot
# Author: Fernando Sanchez (fer@groundcontrol.me)

#dev: activate virtual environment
source venv/bin/activate

#point Flask to the Main app
export FLASK_APP=gopigo-server.py
export FLASK_DEBUG=0


#not needed on a virtual environment#
# for other systems
# sudo pip install -r requirements.txt

#run
flask run --with-threads --host='0.0.0.0'
