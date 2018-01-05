#!/usr/bin/env python
# gopigo-server: a Flask-based REST server to control a GoPiGo Robot

from app import app, db
from app.models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
