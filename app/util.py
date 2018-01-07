from subprocess import call
import datetime
import os.path
import io #to write JPG to file as string

import app
from config import Config
from .models import Document

import picamera, camera

def get_default_iface_name_linux():
    route = "/proc/net/route"
    with open(route) as f:
        for line in f.readlines():
            try:
                iface, dest, _, flags, _, _, _, _, _, _, _, =  line.strip().split()
                if dest != '00000000' or not int(flags, 16) & 2:
                    continue
                return iface
            except:
                continue

def sound(spk):
    #Calls the Espeak TTS Engine to read aloud a sentence
    # This function is going to read aloud some text over the speakers
    #   -ven+m7:    Male voice
    #  The variants are +m1 +m2 +m3 +m4 +m5 +m6 +m7 for male voices and +f1 +f2 +f3 +f4 which simulate female voices by using higher pitches. Other variants include +croak and +whisper.
    #  Run the command espeak --voices for a list of voices.
    #   -s180:      set reading to 180 Words per minute
    #   -k20:       Emphasis on Capital letters
    call(" amixer set PCM 100 ", shell=True)    # Crank up the volume!

    cmd_beg=" espeak -ven-us+m2 -a 200 -s145 -k20 --stdout '"
    cmd_end="' | aplay"
    print cmd_beg+spk+cmd_end
    call ([cmd_beg+spk+cmd_end], shell=True)

def take_photo():
    #Takes a picture from the camera
    #returns the full document object to be stored in DB with the file location
    date_string = str(datetime.datetime.now())
    camera = picamera.PiCamera()
    camera.resolution = (1600, 1200)
    camera.sharpness = 100
    date_string = 'image'+date_string+'.jpg'
    date_string = date_string.replace(":", "")  # Strip out the colon from date time.
    date_string = date_string.replace(" ", "")  # Strip out the space from date time.
    file_location = os.path.join(Config.MEDIA_FOLDER, date_string)
    camera.capture( file_location )
    camera.close()  # We need to close off the resources or we'll get an error.
    #    call([" cp /home/pi/image.jpg "+"/home/pi/"+date_string], shell=True)
    #prepare full document inc. metadata for the picture
    document = Document(
        name=os.path.basename(file_location),   #keep extension: useful to look for it statically
                                                #otherwise remove with:
                                                #os.path.splitext(filename)[0],
        type="picture",
        extension=os.path.splitext(file_location)[1],
        size=os.path.getsize(file_location),
        user_id="",  #out of scope of this module, fill in views
        location=file_location,
        body=""      #don't store in memory yet, in views it's filled from disk
    )

    return document

def yield_video_frames(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def take_photo_from_last_frame(camera):
    """Creates a picture document with the last frame received in the camera"""
    frame = camera.get_frame()
    date_string = str(datetime.datetime.now())
    date_string = 'image'+date_string+'.jpg'
    date_string = date_string.replace(":", "")  # Strip out the colon from date time.
    date_string = date_string.replace(" ", "")  # Strip out the space from date time.

    #save frame to file for temp storage and display
    file_location = os.path.join(Config.MEDIA_FOLDER, date_string)
    print('**DEBUG: writing file to {}'.format(file_location))
    with open (file_location, 'wb') as file:
        file.write(frame)
    file.close()
    print('**DEBUG: written {}'.format(file_location))

    document = Document(
        name=os.path.basename(file_location),   #keep extension: useful to look for it statically
                                                #otherwise remove with:
                                                #os.path.splitext(filename)[0],
        type="picture",
        extension=os.path.splitext(file_location)[1],
        size=os.path.getsize(file_location),
        user_id="",  #out of scope of this module, fill in views
        location=file_location,
        body=""      #don't store in memory yet, in views it's filled from disk
    )

    return document
