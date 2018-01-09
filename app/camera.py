import io
import time
import picamera
from .base_camera import BaseCamera
from config import Config

class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            camera.resolution = Config.CAMERA_RES
            camera.sharpness = Config.CAMERA_SHARPNESS
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
