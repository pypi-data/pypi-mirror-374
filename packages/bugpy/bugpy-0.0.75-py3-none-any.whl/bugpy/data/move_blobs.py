""" Functions for moving files between/within or deleting files from s3 buckets """

from bugpy.utils import multithread, get_credentials
from functools import partial
import pandas as pd
import boto3
from botocore.client import Config
import os


def _delete_one_file(file, bucket, s3_client, verbose=False):
    """For use in multithreaded processes - deletes one file from s3"""

    try:
        s3_client.Object(bucket, file).delete()
    except Exception as e:
        if verbose:
            print("Delete error!")
            print(f"file: {file}")
            print(f"bucket: {bucket}")
        raise e


def _copy_one_file(input_file, from_bucket, to_bucket, prefix='', verbose=False):
    """For use in multithreaded processes - copies a file from one s3 bucket to another"""

    from_file, to_file = input_file
    copy_source = {
        'Bucket': from_bucket.name,
        'Key': from_file
    }

    try:
        to_bucket.copy(copy_source, os.path.join(prefix, to_file))
    except Exception as e:
        if verbose:
            print(f"input_file: {input_file}")
            print(f"copy_source: {copy_source}")
            print(f"to_file: {to_file}")
            print(f"from_file: {from_file}")
            print(f"to_bucket: {to_bucket}")
        raise e


def move_one_file(input_file, from_bucket, to_bucket, s3=None, prefix='', verbose=False, extension=None):
    """
    Move a single file from one S3 bucket to another.

    :param input_file: Tuple of source and destination filenames.
    :type input_file: tuple(str, str)
    :param from_bucket: Name or Boto3 Bucket object of the source bucket.
    :type from_bucket: str or boto3.resources.factory.s3.Bucket
    :param to_bucket: Name or Boto3 Bucket object of the destination bucket.
    :type to_bucket: str or boto3.resources.factory.s3.Bucket
    :param s3: Optional Boto3 S3 resource, auto-initialized if None.
    :type s3: boto3.resources.base.ServiceResource or None
    :param prefix: Prefix to prepend to the destination filename.
    :type prefix: str
    :param verbose: Whether to print detailed output.
    :type verbose: bool
    :param extension: Unused argument placeholder.
    :type extension: str or None
    """

    if s3 is None:
        s3 = boto3.resource('s3', aws_access_key_id=get_credentials('s3', 'API_KEY'),
                            aws_secret_access_key=get_credentials('s3', 'SECRET_KEY'),
                            endpoint_url=get_credentials('s3', 'ENDPOINT'))
        session = boto3.Session()
        s3_client = session.client("s3", config=Config(max_pool_connections=os.cpu_count()),
                                endpoint_url=os.environ['ENDPOINT'],
                                aws_access_key_id=os.environ['API_KEY'],
                                aws_secret_access_key=os.environ['SECRET_KEY'])

    if type(to_bucket) == str:
        to_bucket = s3.Bucket(to_bucket)

    if type(from_bucket) == str:
        from_bucket = s3.Bucket(from_bucket)

    from_file, to_file = input_file

    _copy_one_file(input_file, from_bucket, to_bucket, extension, prefix, verbose, s3_client)
    _delete_one_file(from_file, from_bucket, s3, verbose)


def copy_files(sourcelist, destlist, from_bucket, to_bucket, prefix=''):
    """
    Copy multiple files from one S3 bucket to another.

    :param sourcelist: List of source filenames.
    :type sourcelist: list[str]
    :param destlist: List of destination filenames.
    :type destlist: list[str]
    :param from_bucket: Name of the source bucket.
    :type from_bucket: str
    :param to_bucket: Name of the destination bucket.
    :type to_bucket: str
    :param prefix: Optional prefix for destination files.
    :type prefix: str
    :return: List of files that failed to copy.
    :rtype: list
    """

    if len(sourcelist) != len(destlist):
        raise Exception("sourcelist and destlist must be the same length!")

    s3 = boto3.resource('s3', aws_access_key_id=get_credentials('s3', 'API_KEY'),
                        aws_secret_access_key=get_credentials('s3', 'SECRET_KEY'),
                        endpoint_url=get_credentials('s3', 'ENDPOINT'))

    to_bucket = s3.Bucket(to_bucket)
    to_bucket = s3.Bucket(to_bucket)
    from_bucket = s3.Bucket(from_bucket)

    func = partial(_copy_one_file, from_bucket=from_bucket, to_bucket=to_bucket,
                   prefix=prefix)

    inputs = pd.Series(zip(sourcelist, destlist))

    failures, outputs = multithread(inputs, func,
                                    description=f"Copying files from {from_bucket.name} to {to_bucket.name}")

    if len(failures) > 0:
        print(f"Copied {len(inputs) - len(failures)} files with {len(failures)} failures.")

    return failures


def delete_files(filelist, bucket, s3=None):
    """
    Delete multiple files from a single S3 bucket.

    :param filelist: List of filenames to delete.
    :type filelist: list[str]
    :param bucket: Name of the bucket to delete from.
    :type bucket: str
    :param s3: Optional Boto3 S3 resource, auto-initialized if None.
    :type s3: boto3.resources.base.ServiceResource or None
    :return: List of files that failed to delete.
    :rtype: list
    """

    if s3 is None:
        s3 = boto3.resource('s3', aws_access_key_id=get_credentials('s3', 'API_KEY'),
                            aws_secret_access_key=get_credentials('s3', 'SECRET_KEY'),
                            endpoint_url=get_credentials('s3', 'ENDPOINT'))

    func = partial(_delete_one_file, bucket=bucket, s3_client=s3)

    failures, successes = multithread(filelist, func, description=f"Deleting files from {bucket}")

    if len(failures) > 0:
        print(f"Deleted {len(successes)} files with {len(failures)} failures.")

    return failures


def move_files(sourcelist, destlist, from_bucket, to_bucket, prefix='', s3=None, verbose=False):
    """
    Move multiple files from one S3 bucket to another.

    :param sourcelist: List of source filenames.
    :type sourcelist: list[str]
    :param destlist: List of destination filenames.
    :type destlist: list[str]
    :param from_bucket: Name of the source bucket.
    :type from_bucket: str
    :param to_bucket: Name of the destination bucket.
    :type to_bucket: str
    :param prefix: Optional prefix for destination files.
    :type prefix: str
    :param s3: Optional Boto3 S3 resource, auto-initialized if None.
    :type s3: boto3.resources.base.ServiceResource or None
    :param verbose: Whether to print detailed output, defaults to False.
    :type verbose: bool
    :return: List of files that failed to move.
    :rtype: list
    """

    if s3 is None:
        s3 = boto3.resource('s3', aws_access_key_id=get_credentials('s3', 'API_KEY'),
                            aws_secret_access_key=get_credentials('s3', 'SECRET_KEY'),
                            endpoint_url=get_credentials('s3', 'ENDPOINT'))

    destbucket = s3.Bucket(to_bucket)

    func = partial(move_one_file, from_bucket=from_bucket, to_bucket=destbucket, s3=s3, prefix=prefix, verbose=verbose)

    inputs = pd.Series(zip(sourcelist, destlist))

    failures = multithread(inputs, func, description=f"Moving files from {from_bucket} to {to_bucket}")

    if len(failures) > 0:
        print(f"Moved {len(inputs) - len(failures)} files with {len(failures)} failures.")

    return failures
