import boto3
import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

session = boto3.session.Session()
bucket_name = os.environ.get("BUCKET_NAME")
region = os.environ.get("REGION_NAME")
endpoint_url = os.environ.get("ENDPOINT_URL") or None
client = session.client('s3', region_name=region, endpoint_url=endpoint_url)


def upload_datafile(local_path, cloud_path):
    try:
        client.upload_file(str(local_path), bucket_name,  cloud_path) 
        return True
    except Exception as e:
        print('Failed to Upload DataFile: ', e)
        return False



