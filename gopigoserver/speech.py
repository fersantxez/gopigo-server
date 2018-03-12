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
Classes for speech interaction
Shamelessly copied from:
https://github.com/google/aiyprojects-raspbian/blob/aiyprojects/src/aiy/_apis/_speech.py
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

from abc import abstractmethod
import collections
import logging
import os
import sys
import tempfile
import wave

import google.auth
import google.auth.exceptions
import google.auth.transport.grpc
import google.auth.transport.requests
try:
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
except ImportError:
    print("Failed to import google.cloud.speech. Try:")
    print("    env/bin/pip install -r requirements.txt")
    sys.exit(1)

from google.rpc import code_pb2 as error_code
from google.assistant.embedded.v1alpha1 import embedded_assistant_pb2
import grpc
from six.moves import queue
from six.moves import queue

import gopigoserver.i18n

AUDIO_SAMPLE_SIZE = 2  # bytes per sample
AUDIO_SAMPLE_RATE_HZ = 16000

# Expected location of the service credentials file:
SERVICE_CREDENTIALS = Config.GCP_APPLICATION_DEFAULT_CREDENTIALS_LOCATION  #os.path.expanduser('~/cloud_speech.json')

_Result = collections.namedtuple('_Result', ['transcript', 'response_audio'])


class Error(Exception):
    pass
