#!venv/bin/python
'''
Class to expose the camera to the app.
Shamelessly copied from:
https://blog.miguelgrinberg.com/post/video-streaming-with-flask
https://github.com/miguelgrinberg/flask-video-streaming/blob/master/camera.py
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

import io
import time
import picamera

from gopigoserver.base_camera import BaseCamera


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            camera.resolution = Config.CAMERA_RES
            camera.sharpness = Config.CAMERA_SHARPNESS
            stream = io.BytesIO()
            for _ in camera.capture_continuous(
                    stream, 'jpeg', use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
