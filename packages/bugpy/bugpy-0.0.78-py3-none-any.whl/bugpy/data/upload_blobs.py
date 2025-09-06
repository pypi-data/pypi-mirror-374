""" Functions for uploading files to s3 """
from bugpy.utils import multithread, multiprocess, get_credentials
from botocore.exceptions import ClientError
from botocore.config import Config
from functools import partial
import pandas as pd
import requests
import boto3
import os
from .tools import client_connect, generate_url
from tqdm import tqdm
import time


def upload_with_retries(url, file_path, content_type, max_retries=5):
    for attempt in range(max_retries):
        try:
            with open(file_path, 'rb') as f:
                response = requests.put(
                    url,
                    data=f,
                    headers={"Content-Type": content_type},
                    timeout=(10, 120)
                )

            if response.status_code in [200, 201]:
                return True
            else:
                print(f"Upload failed with status code {response.status_code}")
                print(response.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(2 ** attempt)
    raise Exception(f"Upload failed after {max_retries} attempts: {file_path}")


def upload_one_file(name_tuple: (str, str), bucket: str, s3_client=None, reconnect=True, s3_label='s3_web',
                    force=False) -> str:
    """ Upload a file to an S3 bucket using a presigned URL.

        :param name_tuple: A tuple of (file_location, object_name), where file_location is current location of
        file to upload, object_name is intended name in S3
        :param bucket: Bucket to upload to
        :param s3_client: established s3 connection, autoconnects if None, defaults to None
        :param reconnect: Whether to attempt to create a new s3 session
        :param s3_label: the name of the credential group for s3 connection
        :param force: Force upload even if object exists
        :return: S3 object key
    """
    if reconnect or s3_client is None:
        s3_client = client_connect(cred=s3_label)

    filename, object_name = name_tuple

    if not force:
        try:
            s3_client.head_object(Bucket=bucket, Key=object_name)
            return object_name
        except ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise

    try:
        url, content_type = generate_url(object_name, bucket, s3_client, expire_duration=600)
        upload_with_retries(url, filename, content_type)

    except Exception as e:
        print(f"Error in uploading {filename} to {bucket + '/' + object_name}:")
        print(e)
        raise

    return object_name


def upload_filelist(filelist, aws_bucket=None, upload_dir=None, uploadnames=None, retry_attempts=50, retry=True,
                    s3_label='s3_web', force_reupload=False, parallel=True) -> list:
    """ Uploads a list of local files

        :param filelist: iterable of file names in local storage to be uploaded
        :param aws_bucket: name of S3 bucket where files are hosted
        :param upload_dir: dir to store the files, optional
        :param uploadnames: list of directory locations/names of the uploaded files
        :param retry_attempts: number of times to retry uploads
        :param retry: retries failed uploads one time
        :param s3_label: the name of the credential group for s3 connection
        :param force_reupload: whether to forcably reupload data if already uploaded
        :param parallel: whether to use parallel processing
        :return: list of files which failed to upload
    """

    config = Config(
        retries=dict(
            max_attempts=retry_attempts,
            mode='standard'  # enables exponential backoff
        ),
        read_timeout=120,
        connect_timeout=30,
        max_pool_connections=4 * os.cpu_count()
    )

    if aws_bucket is None:
        aws_bucket = get_credentials(s3_label, 'BUCKET')

    session = boto3.Session()
    client = session.client("s3", config=config,
                            endpoint_url=get_credentials(s3_label, 'ENDPOINT'),
                            aws_access_key_id=get_credentials(s3_label, 'API_KEY'),
                            aws_secret_access_key=get_credentials(s3_label, 'SECRET_KEY'))

    filelist = pd.Series(filelist).dropna()

    if uploadnames is None and upload_dir is None:
        raise Exception("Please supply one of: upload_dir, uploadnames")

    if uploadnames is None and upload_dir is not None:
        uploadnames = filelist.apply(lambda col: os.path.join(upload_dir, os.path.basename(col)))

    func = partial(upload_one_file, bucket=aws_bucket, s3_client=client, reconnect=False, s3_label=s3_label,
                   force=force_reupload)

    if len(filelist) == 0:
        return []

    uploadnames = uploadnames.str.replace('\\', '/', regex=False)

    inputs = pd.Series(zip(filelist, uploadnames))

    if parallel:
        failed_uploads, successes = multithread(inputs, func, description="Uploading files to S3", retry=retry)
    else:
        failed_uploads = []
        successes = []
        for input in tqdm(inputs, desc="Uploading files to S3"):
            try:
                func(input)
                successes.append(input)
            except:
                failed_uploads.append(input)
        if retry:
            for input in tqdm(failed_uploads, desc="Uploading files to S3"):
                try:
                    func(input)
                    successes.append(input)
                except:
                    failed_uploads.append(input)

    print(f"Uploaded {len(filelist) - len(failed_uploads)} files with  {len(failed_uploads)} failures.")

    return failed_uploads
