#!venv/bin/python
import config
from app import app
app_options = ",".join(config.Config.APP_RUN_OPTS)
print("**DEBUG: RUNNING THE APP WITH OPTIONS: {}".format(app_options))
app.run(app_options)
