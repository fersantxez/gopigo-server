from config import Config
from google.cloud import storage, vision 
from google.cloud.vision import types

import os
import logging
logger = logging.getLogger(Config.APP_NAME)

#GCS
def list_buckets():
	"""list all storage buckets visible with the active credentials"""
	storage_client = storage.Client()
	bucket_names = list(storage_client.list_buckets())
	return bucket_names

def create_bucket( bucket_name ):
	"""creates a new bucket and returns it"""
	storage_client = storage.Client()
	mybucket = storage_client.create_bucket( bucket_name )
	logger.debug('Bucket {} created.'.format(mybucket.name) )
	return mybucket

def bucket_exists( bucket_name ):
	"""returns True if buckets exists, None otherwise"""
	storage_client = storage.Client()
	return storage_client.exists( bucket_name )

def get_bucket( bucket_name ):
	"""returns the bucket if it exists, None otherwise"""
	storage_client = storage.Client()
	return storage_client.get_bucket( bucket_name )

def blobs_in_bucket():
	"""yields the filenames in the bucket to a maximum of 3.
	Used for getting the pictures for the video screen"""
	storage_client = storage.Client()
	mybucket = storage_client.get_bucket(Config.bucket_name)
	return mybucket.list_blobs()

def upload_file_to_bucket( file ):
	"""uploads a file object to the global bucket stored in Config"""
	storage_client = storage.Client()
	mybucket = storage_client.get_bucket(Config.bucket_name)
	file_name = os.path.basename(file.name)
	logger.debug('GCS: about to upload {} as {} '.format(file, file_name))
	blob = storage.Blob( file_name, mybucket )
	logger.debug('GCS: created blob {} '.format(blob.name))
	blob.upload_from_file( file )
	logger.debug('GCS: uploaded {} '.format(blob.name))

def delete_file_from_bucket( file_name ):
	"""deletes a file from the global bucket stored in Config"""
	storage_client = storage.Client()
	mybucket = storage_client.get_bucket(Config.bucket_name)
	blob = storage.Blob( file_name, mybucket )
	blob.delete()

def read_file_from_bucket( file_name, dest_file ):
	"""reads into memory a file read from a bucket and returns it as file"""
	storage_client = storage.Client()
	mybucket = storage_client.get_bucket(Config.bucket_name)
	blob = storage.Blob( file_name, mybucket )
	blob.download_to_file( dest_file )
	return dest_file

def create_uri_from_name( file_name ):
	"""creates the full GCS URI from the file name"""
	uri = 'gs://'+\
		Config.bucket_name+\
		'/'+\
		file_name
	logger.debug('URI is: {}'.format( uri ))
	return uri

#Vision API
def vision_api( picture, feature ):
	""" run an image that resides in a bucket through the vision API. Speciy the feature (face or label detecion etc.) """
	picture_uri = create_uri_from_name( picture )
	client = vision.ImageAnnotatorClient()
	#feat_type = 'vision.enums.Feature.Type.'+feature. #FIXME: locate the right enum with the "feature" that indexes it
	try:
		response = client.annotate_image({
			'image': {'source': {'image_uri': picture_uri}},
			'features': [{'type': feature }],			#FIXME: vision.enums.Feature.Type.FACE_DETECTION}],
			})
		logger.debug('Received response is: {}'.format(response))
		return response.annotations
	except Exception as exc:
		logger.error('ERROR calling Google Vision API for picture {}: {}'.format(picture, str(exc)))
		flash('ERROR calling Google Vision API for document {}: {}'.format(picture, str(exc)), 'error')



