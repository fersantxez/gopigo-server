from subprocess import call
import datetime
import os
import io #to write JPG to file as string
import logging
import fcntl, socket, struct

from app import db
from config import Config
from .models import Document
import gcp

import picamera, camera

logger = logging.getLogger(Config.APP_NAME)

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

def get_iface_mac_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])

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

def filename_from_date( file_type, extension ):
    """Generate a filename for a media file based on the current time"""
    date_string = str(datetime.datetime.now())
    date_string = file_type+'-'+date_string+'.'+extension
    date_string = date_string.replace(":", "")  # Strip out the colon from date time.
    date_string = date_string.replace(" ", "")  # Strip out the space from date time.

    return date_string

def create_document_from_file( path, type, user_id ):
    """create an object with all the metadata from a file.
    Uploads it to the database as a full object"""

    logger.debug('Creating document from file {}'.format(path))
    try:
        with open(path, 'rb') as input_file:
            #store the file in GCS
            logger.debug('file {} opened'.format(path))
            filename = os.path.basename(path)
            gcp.upload_file_to_bucket( input_file )
            document = Document(
                name=filename,   #keep extension: useful to look for it statically
                                                        #otherwise remove with:
                                                        #os.path.splitext(filename)[0],
                type=type,
                extension=os.path.splitext(path)[1],
                size=os.path.getsize(path),
                user_id=user_id,  
                location=gcp.create_uri_from_name( filename )   #store the object's URI instead of the file path,
                #,body=None     #body is empty in DB and stored in GCS, instead of storing the full doc with: 
                #input_file.read()
                )
        input_file.close()
        db.session.add(document)
        db.session.commit()
        if not path == Config.EMPTY_PICTURE: 
            os.remove(path)   #FIXME: emove the file from local disk
        return document

    except Exception as exc:
        db.session.rollback()
        logger.error('ERROR uploading document {}: {}'.format(path, str(exc)))

def take_photo():
    #Takes a picture from the camera
    #returns the location of the file created. 
    #this is BLOCKING so it can't be used simultaneously with the streaming. For 
    #that, use take_photo_from_last_frame below
    date_string = str(datetime.datetime.now())
    camera = picamera.PiCamera()
    camera.resolution = (Config.CAMERA_RES_X, Config.CAMERA_RES_Y)
    camera.sharpness = Config.CAMERA_SHARPNESS
    file_location = os.path.join(Config.MEDIA_FOLDER, filename_from_date)
    camera.capture( file_location )
    camera.close()  # We need to close off the resources or we'll get an error.

    return file_location
    
def take_photo_from_last_frame(camera):
    """Creates a picture document with the last frame received in the camera"""
    frame = camera.get_frame()
    #save frame to file for temp storage and display
    file_location = os.path.join(Config.MEDIA_FOLDER, filename_from_date( 'picture', 'jpg'))
    logger.debug('Writing file to {}'.format(file_location))
    with open (file_location, 'wb') as file:
        file.write(frame)
    file.close()
    logger.debug('Written file {}'.format(file_location))

    return file_location

def yield_video_frames(camera):
    """Video streaming generator function."""
    while True:
        try:
            frame = camera.get_frame()
        except IOError:
            pass
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')









