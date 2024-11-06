import os
import time
from google.cloud import storage

# Set the path to your Google Cloud service account JSON key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\Studium\\Semester5\\Big Data\\bigdatalecture-437214-bdbda9126644.json"

# Replace with your Google Cloud project and bucket name
PROJECT_ID = "bigdatalecture-437214"
BUCKET_NAME = "bigdatalecture_mtg_dl"
FILE_NAME = "raw_mtg_cards.json"  # Destination file name in GCS

# Initialize the Google Cloud Storage client
storage_client = storage.Client(project=PROJECT_ID)

# Function to upload a file to Google Cloud Storage
def upload_to_gcs(file_path, bucket_name, destination_blob_name):
    try:
        start_time = time.time()  # Start time for data retrieval
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Check if the file exists before uploading
        if os.path.exists(file_path):
            blob.upload_from_filename(file_path)
            print(f"File {file_path} uploaded to {destination_blob_name}.")
        else:
            print(f"File {file_path} does not exist. Please check the file path.")

        ingestion_time = time.time() - start_time  # Calculate ingestion time
        print(f"Data ingestion completed in {ingestion_time:.2f} seconds.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Get the directory of the current script and build the path to data.json
script_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(script_dir, "data.json")

# Set the destination path in GCS (raw_data folder)
destination_blob_name = "raw_data/raw_mtg_cards.json"

# Call the function to upload the file
upload_to_gcs(file_path, BUCKET_NAME, destination_blob_name)
