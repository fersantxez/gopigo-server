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

"""Drivers for audio functionality."""

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

import time
import wave
import sys
import tempfile
import functools
import subprocess
import os

import app.player
import app.recorder
import app.i18n

AUDIO_SAMPLE_SIZE = Config.AUDIO_SAMPLE_SIZE  # bytes per sample
AUDIO_SAMPLE_RATE_HZ = Config.AUDIO_SAMPLE_RATE_HZ

# Global variables. They are lazily initialized.
_gopigo_recorder = None
_gopigo_player = None
_tts_volume = Config.TTS_VOLUME
_tts_pitch = Config.TTS_PITCH


class _WaveDump(object):
    """A processor that saves recorded audio to a wave file."""

    def __init__(self, filepath, duration):
        self._wave = wave.open(filepath, 'wb')
        self._wave.setnchannels(1)
        self._wave.setsampwidth(2)
        self._wave.setframerate(16000)
        self._bytes = 0
        self._bytes_limit = int(duration * 16000) * 1 * 2

    def add_data(self, data):
        max_bytes = self._bytes_limit - self._bytes
        data = data[:max_bytes]
        self._bytes += len(data)
        if data:
            self._wave.writeframes(data)

    def is_done(self):
        return self._bytes >= self._bytes_limit

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._wave.close()


def get_player():
    """Returns a driver to control the gopigo speaker.

    The aiy modules automatically use this player. So usually you do not need to
    use this. Instead, use 'aiy.audio.play_wave' if you would like to play some
    audio.
    """
    global _gopigo_player
    if not _gopigo_player:
        _gopigo_player = app.player.Player()
        logger.debug("created a new player: {}".format(_gopigo_player))
    return _gopigo_player


def get_recorder():
    """Returns a driver to control the gopigo microphone.

    The aiy modules automatically use this recorder. So usually you do not need to
    use this.
    """
    global _gopigo_recorder
    if not _gopigo_recorder:
        _gopigo_recorder = app.recorder.Recorder()
    return _gopigo_recorder


def record_to_wave(filepath, duration):
    """Records an audio for the given duration to a wave file."""
    recorder = get_recorder()
    dumper = _WaveDump(filepath, duration)
    with recorder, dumper:
        recorder.add_processor(dumper)
        while not dumper.is_done():
            time.sleep(0.1)


def play_wave(wave_file):
    """Plays the given wave file.

    The wave file has to be mono and small enough to be loaded in memory.
    """
    player = get_player()
    player.play_wav(wave_file)


def play_audio(audio_data):
    """Plays the given audio data."""
    player = get_player()
    player.play_bytes(audio_data, sample_width=AUDIO_SAMPLE_SIZE, sample_rate=AUDIO_SAMPLE_RATE_HZ)

def set_tts_volume(volume):
    global _tts_volume
    _tts_volume = volume


def get_tts_volume():
    global _tts_volume
    return _tts_volume


def set_tts_pitch(pitch):
    global _tts_pitch
    _tts_pitch = pitch


def get_tts_pitch():
    global _tts_pitch
    return _tts_pitch


def say(words, lang=Config.TTS_LANGUAGE, volume=_tts_volume, pitch=_tts_pitch):
    """Says the given words in the given language with TTS engine.
    #Calls the Espeak TTS Engine to read aloud a sentence
    # This function is going to read aloud some text over the speakers
    #   -ven+m7:    Male voice
    #  The variants are +m1 +m2 +m3 +m4 +m5 +m6 +m7 for male voices and +f1 +f2 +f3 +f4 which simulate female voices by using higher pitches. Other variants include +croak and +whisper.
    #  Run the command espeak --voices for a list of voices.
    #   -s180:      set reading to 180 Words per minute
    #   -k20:       Emphasis on Capital letters
    """
    if not lang:
        lang = app.i18n.get_language_code()
        logger.debug("got lang from i18n: {}".format(lang))
    if not volume:
        #volume = app.audio.get_tts_volume() #these are globals, access with full path (app.audio.XXX)
        volume = app.audio.get_tts_volume()
        logger.debug("got volume from myself: {}".format(volume))
    if not pitch:
        #pitch = app.audio.get_tts_pitch()
        pitch = app.audio.get_tts_pitch()
        logger.debug("got pitch from myself: {}".format(pitch))
    logger.debug("About to SAY the words: {}".format(words))
    #create player
    player = app.audio.get_player()
    logger.debug("I've got a Player that looks like: {}".format(player))
    #create buffer file and send to player
    try:
        (fd, tts_wav) = tempfile.mkstemp(suffix='.wav', dir=Config.MEDIA_DIR) #FIXME: use media dir, then upload to Cloud?
    except IOError:
        logger.exception('Using fallback directory for TTS output')
        (fd, tts_wav) = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    logger.debug('have a file {} to use as buffer in {}'.format(fd, tts_wav))
    #configure the voice and say something through espeak
    voice=Config.TTS_VOICE
    langvoice=str(lang)+"+"+voice       #espeak format "-ven-us+m2"
    emphasis='-k'+'20'                  #emphasis on capital letters
    try:
        #subprocess.call(['pico2wave', '--lang', lang, '-w', tts_wav, words])
        logger.debug('Calling espeak to say the words: {} to file {}'.format(words, tts_wav))
        subprocess.call(['espeak', '-v', langvoice, '-a', str(volume), '-s', str(pitch), '-k', emphasis, '-w', tts_wav, words])
        logger.debug('about to call the Player to "read" from the file {} the words: {}'.format(tts_wav, words))
        player.play_wav(tts_wav) #not fd which is the descriptor
    finally:
        os.unlink(tts_wav)

def listen(filepath, duration):
    """record for a given number of seconds"""
    #FIXME: add volume
    app.audio.record_to_wave(filepath, duration)
