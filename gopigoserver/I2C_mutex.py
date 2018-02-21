#!venv/bin/python

'''
Class to control the interface with the GoPiGo I2C.
I2C is a shared bus with multiple devices, which could be accessed from multiple processes as well as threads. 
So the Linux I2C driver code uses a mutex to manage access to each I2C bus.
Shamelessly copied from:
https://github.com/DexterInd/GoPiGo/blob/master/Software/Python/I2C_mutex.py
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

import fcntl
import time

class Mutex(object):

    DexterLockI2C_handle = None

    def __init__(self, debug = False):
        self.mutex_debug = debug

    def acquire(self):
        if self.mutex_debug:
            logger.debug("I2C mutex acquire")

        acquired = False
        while not acquired:
            try:
                self.DexterLockI2C_handle = open('/run/lock/DexterLockI2C', 'w')
                # lock
                fcntl.lockf(self.DexterLockI2C_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except IOError: # already locked by a different process
                time.sleep(0.001)
            except Exception as e:
                print(e)

        if self.mutex_debug:
            logger.debug("I2C mutex acquired {}".format(time.time()))

    def release(self):
        if self.mutex_debug:
            logger.debug("I2C mutex release: {}".format(time.time()))
        if self.DexterLockI2C_handle is not None and self.DexterLockI2C_handle is not True:
            self.DexterLockI2C_handle.close()
            self.DexterLockI2C_handle = None
            time.sleep(0.001)

    def enableDebug(self):
        self.mutex_debug = True

    def disableDebug(self):
        self.mutex_debug = False

    def __enter__(self):
        if self.mutex_debug:
            logger.debug("I2C mutex enter")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.mutex_debug:
            logger.debug("I2C mutex exit")
        self.release()
