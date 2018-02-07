from config import Config
from google.cloud import storage

def list_buckets():
	"""list all storage buckets visible with the active credentials"""

	storage_client = storage.Client()
	buckets = list(storage_client.list_buckets())
	return buckets