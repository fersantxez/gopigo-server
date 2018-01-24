#!venv/bin/python
from config import Config
from app import app
print("**DEBUG: RUNNING THE APP WITH OPTIONS: {}".format(Config.APP_RUN_OPTS))
app.run(**Config.APP_RUN_OPTS)
