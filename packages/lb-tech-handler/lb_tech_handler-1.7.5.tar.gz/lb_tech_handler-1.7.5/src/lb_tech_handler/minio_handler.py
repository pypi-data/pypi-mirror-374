from minio import Minio
from minio.error import S3Error
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

LB_MINIO_ENDPOINT = os.getenv(key='LB_MINIO_ENDPOINT')

LB_MINIO_ACCESS_KEY = os.getenv(key='LB_MINIO_ACCESS_KEY')

LB_MINIO_SECRET_KEY = os.getenv(key='LB_MINIO_SECRET_KEY')

if LB_MINIO_ENDPOINT is None:
    raise Exception("LB_MINIO_ENDPOINT is not set")

if LB_MINIO_ACCESS_KEY is None:
    raise Exception("LB_MINIO_ACCESS_KEY is not set")

if LB_MINIO_SECRET_KEY is None:
    raise Exception("LB_MINIO_SECRET_KEY is not set")


minio_client = Minio(
    endpoint = LB_MINIO_ENDPOINT,
    access_key = LB_MINIO_ACCESS_KEY,
    secret_key = LB_MINIO_SECRET_KEY,
    secure = False
)

def list_all_buckets():
    try:
        return minio_client.list_buckets()
    except S3Error as err:
        raise err
    
def list_all_objects(bucket_name: str, recursive: bool=False):
    try:
        return minio_client.list_objects(bucket_name=bucket_name, recursive=recursive)
    except S3Error as err:
        raise err

def check_object_exists(bucket_name, object_name):
    try:
        return minio_client.stat_object(bucket_name=bucket_name, object_name=object_name)
    except S3Error as err:
        raise err
    
def get_minio_download_url(bucket_name, object_name, extra_params=None):
    try:

        check_object_exists(bucket_name=bucket_name, object_name=object_name)
        
        return minio_client.get_presigned_url(bucket_name=bucket_name, object_name=object_name,method='GET', extra_query_params=extra_params)
    
    except S3Error as err:
        raise err
    
def get_minio_upload_url(bucket_name, object_name):
    try:
        return minio_client.presigned_put_object(bucket_name=bucket_name, object_name=object_name)
    except S3Error as err:
        raise err
    




if __name__ == "__main__":
    link = get_minio_download_url('testing','Exercise on solving equation.mp4')

    print(link)