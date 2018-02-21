#!venv/bin/python
from config import Config
from gopigoserver import app

import logging
logger = logging.getLogger(Config.APP_NAME)

logger.debug("RUNNING THE APP WITH OPTIONS: {}".format(Config.APP_RUN_OPTS))
app.run(**Config.APP_RUN_OPTS)
