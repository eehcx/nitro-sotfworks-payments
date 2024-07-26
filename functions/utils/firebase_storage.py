import google.cloud.storage

class Storage:
    @staticmethod
    def upload_to_firebase_storage(file, filename):
        storage_client = google.cloud.storage.Client()
        bucket = storage_client.bucket('users_metadata')

        blob = bucket.blob(filename)
        # Subir el archivo al bucket
        blob.upload_from_file(file, content_type='image/png')
        blob.make_public() 

        return blob.public_url