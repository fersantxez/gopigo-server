from subprocess import call
import datetime
import os
import io #to write JPG to file as string

from app import db
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

def filename_from_date():
    """Generate a filename for a media file based on the current time"""
    date_string = str(datetime.datetime.now())
    date_string = 'image'+date_string+'.jpg'
    date_string = date_string.replace(":", "")  # Strip out the colon from date time.
    date_string = date_string.replace(" ", "")  # Strip out the space from date time.

    return date_string    

def document_from_file( file_path, filetype ):
    """creates an object with all the metadata"""

    document = Document(
        name=os.path.basename(file_path),   #keep extension: useful to look for it statically
                                                #otherwise remove with:
                                                #os.path.splitext(filename)[0],
        type=filetype,
        extension=os.path.splitext(file_path)[1],
        size=os.path.getsize(file_path),
        user_id="",  #out of scope of this module, fill in views
        location=file_path,
        body=""      #don't store in memory yet, in views it's filled from disk
    )

    return document

def put_document_from_file(document):
    """uploads to the database the body of a document from file.
    Deletes the file from disk if successful"""
    try:
        with open(document.location, 'rb') as input_file:
            document.body = input_file.read()
        input_file.close()
        db.session.add(document)
        db.session.commit()
        if os.path.exists(document.location):
                os.remove(document.location)
    except Exception:
        db.session.rollback()
        flash('ERROR uploading document', 'error')
        raise IOError

    return document.location

def take_photo():
    #Takes a picture from the camera
    #returns the full document object to be stored in DB with the file location
    #this is BLOCKING so it can't be used simultaneously with the streaming. For 
    #that, use take_photo_from_last_frame below
    date_string = str(datetime.datetime.now())
    camera = picamera.PiCamera()
    camera.resolution = (Config.CAMERA_RES_X, Config.CAMERA_RES_Y)
    camera.sharpness = Config.CAMERA_SHARPNESS
    file_location = os.path.join(Config.MEDIA_FOLDER, filename_from_date)
    camera.capture( file_location )
    camera.close()  # We need to close off the resources or we'll get an error.
    #prepare full document inc. metadata for the picture
    document = document_from_file( file_location, "picture" )

    return document

def take_photo_from_last_frame(camera):
    """Creates a picture document with the last frame received in the camera"""
    frame = camera.get_frame()
    #save frame to file for temp storage and display
    file_location = os.path.join(Config.MEDIA_FOLDER, filename_from_date())
    print('**DEBUG: writing file to {}'.format(file_location))
    with open (file_location, 'wb') as file:
        file.write(frame)
    file.close()
    print('**DEBUG: written {}'.format(file_location))
    document = document_from_file( file_location, "picture" )

    return document

def yield_video_frames(camera):
    """Video streaming generator function."""
    while True:
        try:
            frame = camera.get_frame()
        except IOError:
            pass
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')









