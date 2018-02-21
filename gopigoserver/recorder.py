#!venv/bin/python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
A recorder driver capable of recording voice samples from the VoiceHat microphones.
Shamelessly copied from:
https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/aiy/_drivers/_recorder.py
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

import os
import subprocess
import threading
import sys

from gopigoserver.alsa import sample_width_to_string


class Recorder(threading.Thread):
    """A driver to record audio from the VoiceHat microphones.

    Stream audio from microphone in a background thread and run processing
    callbacks. It reads audio in a configurable format from the microphone,
    then converts it to a known format before passing it to the processors.

    This driver accumulates input (audio samples) in a local buffer. Once the
    buffer contains more than CHUNK_S seconds, it passes the chunk to all
    processors. An audio processor defines a 'add_data' method that receives
    the chunk of audio samples to process.
    """

    CHUNK_S = 0.1

    def __init__(self, input_device=Config.RECORDING_DEVICE,
                 channels=1, bytes_per_sample=Config.AUDIO_SAMPLE_SIZE, sample_rate_hz=Config.AUDIO_SAMPLE_RATE_HZ):
        """Create a Recorder with the given audio format.

        The Recorder will not start until start() is called. start() is called
        automatically if the Recorder is used in a `with`-statement.

        - input_device: name of ALSA device (for a list, run `arecord -L`)
        - channels: number of channels in audio read from the mic
        - bytes_per_sample: sample width in bytes (eg 2 for 16-bit audio)
        - sample_rate_hz: sample rate in hertz
        """

        #FIXME: Python 2 vs python 3
        #super(Recorder, self).__init__()   #python2 OK
        #self.setDaemon(True)               #python2
        #super(Recorder).init()             #python2 NOK
        super().__init__(daemon=True)       #python3

        self._processors = []

        self._chunk_bytes = int(self.CHUNK_S * sample_rate_hz) * channels * bytes_per_sample

        self._cmd = [
            'arecord',
            '-q',
            '-t', 'raw',
            '-D', input_device,
            '-c', str(channels),
            # pylint: disable=W0212
            '-f', sample_width_to_string(bytes_per_sample),
            '-r', str(sample_rate_hz),
        ]
        self._arecord = None
        self._closed = False
        logger.debug('Recording Thread INIT completed...')

    def add_processor(self, processor):
        """Add an audio processor.

        An audio processor is an object that has an 'add_data' method with the
        following signature:
        class MyProcessor(object):
          def __init__(self):
            ...

          def add_data(self, data):
            # processes the chunk of data here.

        The added processor may be called multiple times with chunks of audio data.
        """
        self._processors.append(processor)

    def remove_processor(self, processor):
        """Remove an added audio processor."""
        try:
            self._processors.remove(processor)
        except ValueError:
            logger.warn("processor was not found in the list")

    def run(self):
        """Reads data from arecord and passes to processors."""
        logger.debug('About to create and pipe a process to read from stdout on device {}'.format(Config.RECORDING_DEVICE))
        self._arecord = subprocess.Popen(self._cmd, stdout=subprocess.PIPE)
        logger.info("started recording")

        # Check for race-condition when __exit__ is called at the same time as
        # the process is started by the background thread
        if self._closed:
            self._arecord.kill()
            return

        this_chunk = b''

        while True:
            logger.debug('About to read from stdout on device {}'.format(Config.RECORDING_DEVICE))
            input_data = self._arecord.stdout.read(self._chunk_bytes) #FIXME: change to better pipe management
                                        #http://kendriu.com/how-to-use-pipes-in-python-subprocesspopen-objects
            if not input_data:  #FIXME: apparently this works until the mic doesnt detect signal
                break

            this_chunk += input_data
            if len(this_chunk) >= self._chunk_bytes:
                self._handle_chunk(this_chunk[:self._chunk_bytes])
                this_chunk = this_chunk[self._chunk_bytes:]

        if not self._closed:
            logger.error('Microphone recorder died unexpectedly, aborting...')
            # sys.exit doesn't work from background threads, so use os._exit as
            # an emergency measure.
            logging.shutdown()
            os._exit(1)  # pylint: disable=protected-access

        logger.debug('IM GETTING THE FUCK OUT OF HERE')

    def stop(self):
        """Stops the recorder and cleans up all resources."""
        self._closed = True
        if self._arecord:
            self._arecord.kill()
        logger.debug('STOPPED recording thread')

    def _handle_chunk(self, chunk):
        """Send audio chunk to all processors."""
        for p in self._processors:
            p.add_data(chunk)

    def __enter__(self):
        #if not self.is_alive():
        print('WHATS UP!!!!')
        logger.debug('OH FUCK IM NOT ALIVE. WHATS UP WITH THAT?')
        self.start()        #FIXME: start only if not existing
        return self

    def __exit__(self, *args):
        logger.debug('EXITING recording thread')
        self.stop()