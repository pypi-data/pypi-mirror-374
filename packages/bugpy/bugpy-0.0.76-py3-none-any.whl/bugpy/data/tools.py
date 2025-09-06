from bugpy.utils import get_credentials
from functools import lru_cache
import mimetypes
import botocore
import boto3
import os
import re
import logging

class ConnectionPoolLimitFilter(logging.Filter):
    def filter(self, record):
        return "Max pool connections" in record.getMessage()

# Create a custom logger
logger = logging.getLogger('botocore.endpoint')
logger.setLevel(logging.WARNING)  # or INFO if needed

# Add a handler for just pool limit warnings
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
handler.addFilter(ConnectionPoolLimitFilter())

formatter = logging.Formatter('[POOL WARNING] %(asctime)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

@lru_cache(maxsize=1)
def client_connect(connection_pool=None, cred='s3_web', config=None):
    """ Makes a s3 connection

        :param connection_pool: connection pool size, defaults to your CPU count
        :return: s3 client
    """

    if connection_pool is None:
        connection_pool = os.cpu_count()*4
    if config is None:
        config = botocore.client.Config(
            retries=dict(max_attempts=5, mode='standard'),
            read_timeout=300,
            connect_timeout=30,
            max_pool_connections=connection_pool
        )
    s3_client = boto3.client('s3', config=config,
                             aws_access_key_id=get_credentials(cred, 'API_KEY'),
                             aws_secret_access_key=get_credentials(cred, 'SECRET_KEY'),
                             endpoint_url=get_credentials(cred, 'ENDPOINT'))
    return s3_client


def resource_connect(cred='s3_web'):
    """ Makes a s3 connection

        :return: s3 resource
    """

    s3_client = boto3.resource('s3',
                               aws_access_key_id=get_credentials(cred, 'API_KEY'),
                               aws_secret_access_key=get_credentials(cred, 'SECRET_KEY'),
                               endpoint_url=get_credentials(cred, 'ENDPOINT'))
    return s3_client


def flatten_filepath(input_string) -> str:
    """ Replaces folder structure with _ character

        :param input_string: string to be formatted
        :return: formatted string
    """
    output_string = re.sub('/', '_', input_string)

    return output_string


def join_filepath(pathlist):
    pathlist = [x.replace('\\', '/') for x in pathlist]
    return ('/'.join(pathlist)).replace('//', '/')


def generate_url(object_name, bucket, s3_client, expire_duration=604800):
    content_type, _ = mimetypes.guess_type(object_name)
    if content_type is None:
        content_type = "application/octet-stream"  # Fallback for unknown types
    url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket,
            'Key': object_name,
            'ContentType': content_type
        },
        ExpiresIn=expire_duration
    )
    return url, content_type