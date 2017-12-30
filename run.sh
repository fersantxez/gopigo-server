#!/bin/bash

# gopigo-server: a Flask-based REST server to control a GoPiGo Robot
# Author: Fernando Sanchez (fer@groundcontrol.me)

#activate virtual environment
source venv/bin/activate

#point Flask to the Main app
export FLASK_APP=gopigo-server.py
export FLASK_DEBUG=1

#ensure requirements are met
#not needed on a virtual environment#
#pip install -r requirements.txt

#run
flask run
