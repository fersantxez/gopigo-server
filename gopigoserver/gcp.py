#!venv/bin/python

'''
Helpers and utils to communicate with different GCP services.
Google Cloud Storage
Google Cloud Vision API
Google Cloud Speech API
FIXME: should probably split in separate meaningful modules/classes.
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

import os
import re       #for cleaning special chars from strings

from google.cloud import storage, vision, speech 
#from google.cloud.vision import types
from google.cloud.speech import enums, types

import gopigoserver.audio


#####################
#  Cloud Storage    #
#####################

def list_buckets():
    '''
    list all storage buckets visible with the active credentials
    '''
    storage_client = storage.Client()
    bucket_names = list(storage_client.list_buckets())
    return bucket_names


def create_bucket( bucket_name ):
    '''
    creates a new bucket and returns it
    '''
    storage_client = storage.Client()
    mybucket = storage_client.create_bucket( bucket_name )
    logger.debug('Bucket {} created.'.format(mybucket.name) )
    return mybucket


def bucket_exists( bucket_name ):
    '''
    returns True if buckets exists, None otherwise
    '''
    storage_client = storage.Client()
    return storage_client.exists( bucket_name )


def get_bucket( bucket_name ):
    '''
    returns the bucket if it exists, None otherwise
    '''
    storage_client = storage.Client()
    return storage_client.get_bucket( bucket_name )


def blobs_in_bucket():
    '''
    yields the filenames in the bucket to a maximum of 3.
    Used for getting the pictures for the video screen
    '''
    storage_client = storage.Client()
    mybucket = storage_client.get_bucket(Config.bucket_name)
    return mybucket.list_blobs()


def upload_file_to_bucket( file ):
    '''
    uploads a file object to the global bucket stored in Config
    '''
    storage_client = storage.Client()
    mybucket = storage_client.get_bucket(Config.bucket_name)
    file_name = os.path.basename(file.name)
    logger.debug('GCS: about to upload {} as {} '.format(file, file_name))
    blob = storage.Blob( file_name, mybucket )
    logger.debug('GCS: created blob {} '.format(blob.name))
    blob.upload_from_file( file )
    logger.debug('GCS: uploaded {} '.format(blob.name))


def delete_file_from_bucket( file_name ):
    '''
    deletes a file from the global bucket stored in Config
    '''
    storage_client = storage.Client()
    mybucket = storage_client.get_bucket(Config.bucket_name)
    blob = storage.Blob( file_name, mybucket )
    blob.delete()


def read_file_from_bucket( file_name, dest_file ):
    '''
    reads into memory a file read from a bucket and returns it as file
    '''
    storage_client = storage.Client()
    mybucket = storage_client.get_bucket(Config.bucket_name)
    blob = storage.Blob( file_name, mybucket )
    blob.download_to_file( dest_file )
    return dest_file


def create_uri_from_name( file_name ):
    '''
    creates the full GCS URI from the file name
    '''
    uri = 'gs://'+\
        Config.bucket_name+\
        '/'+\
        file_name
    logger.debug('URI is: {}'.format( uri ))
    return uri


#####################
#  Vision API       #
#####################

def vision_api( picture, feature, unpack_function_name ):
    '''
    run an image that resides in a bucket through the vision API. Speciy the feature (face or label detecion etc.)
    '''
    picture_uri = create_uri_from_name( picture )
    client = vision.ImageAnnotatorClient()
    #feat_type = 'vision.enums.Feature.Type.'+feature. #FIXME: locate the right enum with the "feature" that indexes it
    try:
        response = client.annotate_image({
            'image': {'source': {'image_uri': picture_uri}},
            'features': [{'type': feature }],           #FIXME: vision.enums.Feature.Type.FACE_DETECTION}],
        })
        #logger.debug('Received response is: {}'.format(response))
        #call each of the Vision API specific subfunctions to unpack
        result = globals()[unpack_function_name](response)      #calls the associated unpack function
        logger.debug('result from FUNCTION {} is: {}'.format(unpack_function_name, result))
        return result
    except Exception as exc:
        logger.error('ERROR calling Google Vision API for picture {}: {}'.format(picture, str(exc)))


def unpack_label_detection( response ):
    '''
    unpack the result of a label detection call, return a list with the labels
    '''
    logger.debug('Called unpack_label with: {}'.format(response))
    result = []
    for annotation in response.label_annotations:
        logger.debug('Found annotation: {}'.format(annotation.description))
        result.append(annotation.description)
    logger.debug('result in unpack_label is: {}'.format(result))
    return result


def unpack_text_detection( response ):
    '''
    unpack the result of a text detection call, return the legible text in a humanly fashion
    '''
    logger.debug('Called unpack_text with: {}'.format(response))
    result = []
    result.append(response.text_annotations[0].description) #the API returns first the entire text then each word
    return result


def unpack_document_text_detection( response ):
    '''
    unpack the result of a document text detection call, return the legible text in a humanly fashion
    '''
    result = []
    text = str(response.full_text_annotation.text)
    clean_text = re.sub('\W+','', text )
    result.append(clean_text)   #the API returns first the entire text then each word
    #for annotation in response.text_annotations:.
    #   logger.debug('Found annotation: {}'.format(annotation.description))
    #   result.append(annotation.description)
    #logger.debug('result in unpack_text is: {}'.format(result))
    return result


def unpack_face_detection( response ):
    '''
    unpack the result of a face detection call, return the faces and features
    '''
    result = []
    faces = response.face_annotations
    for i, face in enumerate(faces): #AnnotateImageResponse' object is not iterable
        logger.debug('Found annotation: {}'.format(i))
        reply = "Person number "+str(i+1)+" shows " #number "+str(i)+"
        reply += ', anger?: {}'.format(Config.LIKELIHOOD_NAME[face.anger_likelihood])
        reply += ', joy?: {}'.format(Config.LIKELIHOOD_NAME[face.joy_likelihood])
        reply += ', sorrow?: {}'.format(Config.LIKELIHOOD_NAME[face.sorrow_likelihood])
        reply += ', surprise?: {}'.format(Config.LIKELIHOOD_NAME[face.surprise_likelihood])
        result.append(reply)
    logger.debug('result in unpack_face_detection is: {}'.format(result))
    return result


def unpack_landmark_detection( response ):
    '''
    unpack the result of a landmark detection call, return the detected landmark
    '''
    logger.debug('Called unpack_landmark with: {}'.format(response))
    result = []
    for annotation in response.landmark_annotations:
        logger.debug('Found annotation: {}'.format(annotation.description))
        result.append(annotation.description)
    logger.debug('result in unpack_landmark is: {}'.format(result))
    return result


def unpack_logo_detection( response ):
    '''
    unpack the result of a logo detection call, return the detected landmark
    '''
    logger.debug('Called unpack_logo with: {}'.format(response))
    result = []
    for annotation in response.logo_annotations:
        logger.debug('Found annotation: {}'.format(annotation.description))
        result.append(annotation.description)
    logger.debug('result in unpack_logo is: {}'.format(result))
    return result


def unpack_safe_search_detection( response ):
    '''
    unpack the result of a safe search detection call, return the detected landmark
    '''
    logger.debug('Called unpack_safe_search with: {}'.format(response))
    result = []
    safe = response.safe_search_annotation
    reply = "The result of safe search on image shows " #number "+str(i)+"
    reply += ', adult?: {}'.format(Config.LIKELIHOOD_NAME[safe.adult])
    reply += ', medical?: {}'.format(Config.LIKELIHOOD_NAME[safe.medical])
    reply += ', spoofed?: {}'.format(Config.LIKELIHOOD_NAME[safe.spoof])
    reply += ', violence?: {}'.format(Config.LIKELIHOOD_NAME[safe.violence])
    result.append(reply)
    logger.debug('result in unpack_face_detection is: {}'.format(result))
    return result


def unpack_image_properties( response ):
    '''
    unpack the result of a safe search detection call, return the detected landmark
    '''
    logger.debug('Called unpack_image_properties with: {}'.format(response))
    result = []
    props = response.image_properties_annotation
    for color in props.dominant_colors.colors:
        reply = "The result of image detection properties on image shows " #number "+str(i)+"
        reply += ', fraction: {}'.format(color.pixel_fraction)
        reply += ', red: {}'.format(color.color.red)
        reply += ', green: {}'.format(color.color.green)
        reply += ', blue: {}'.format(color.color.blue)
        reply += ', alpha: {}'.format(color.color.alpha)
    result.append(reply)
    logger.debug('result in unpack_image_properties is: {}'.format(result))
    return result


#####################
#  Speech API       #
#####################

