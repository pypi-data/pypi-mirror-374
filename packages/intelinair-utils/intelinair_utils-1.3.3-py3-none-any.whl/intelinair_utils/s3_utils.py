"""Collection of general utility functions"""
import logging
import multiprocessing
import os
from pathlib import Path
from typing import Tuple, Union
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from tenacity import retry, wait_exponential, retry_if_exception_type, stop_after_attempt

from intelinair_utils.retry_utils import log_after_first_attempt


__all__ = [
    'split_s3_path',
    'download_s3_file',
    's3_file_exists',
    'upload_s3_file',
    'download_from_s3',
    'upload_to_s3',
    'delete_s3_file',
    'get_list_of_s3_files'
]

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

logger = logging.getLogger(__name__)


def split_s3_path(s3_path: str) -> Tuple[str, str]:
    """Splits an s3 path into its bucket and key

    Args:
        s3_path: as s3 uri to split ex: 's3://your-bucket/your/key'

    Returns:
        bucket: the s3 bucket your object is located in
        key: the key of your object
    """
    if s3_path.startswith('https://s3.amazonaws.com/'):
        s3_path = s3_path.replace('https://s3.amazonaws.com/', 's3://')
    assert 's3://' == s3_path[0:5]
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)

    return bucket, key


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(3), retry=retry_if_exception_type(ClientError),
       reraise=True, after=log_after_first_attempt)
def download_s3_file(s3_path: str, output_path: Union[str, Path]) -> None:
    """Downloads the file from s3 to the given path."""
    logger.info(f'Downloading {s3_path} to {output_path}')

    output_path = Path(output_path).expanduser()
    bucket, key = split_s3_path(s3_path)

    if output_path.is_dir():
        output_path = output_path.joinpath(key.split('/')[-1])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    s3_client.download_file(bucket, key, output_path.as_posix())


def download_from_s3(s3_path: str, local_path: Union[str, Path], num_processes: int = 8) -> None:
    """Downloads either a file or directory from s3"""
    local_path = Path(local_path)

    if s3_file_exists(s3_path) and not s3_path.endswith('/'):  # is actually a file
        return download_s3_file(s3_path, local_path.as_posix())

    def generate_args():
        bucket, prefix = split_s3_path(s3_path)
        bucket = s3_resource.Bucket(bucket)
        for obj in bucket.objects.filter(Prefix=prefix):
            if obj.key[-1] == '/':
                continue
            target = local_path.joinpath(obj.key.replace(prefix, '').lstrip('/'))
            yield f's3://{bucket.name}/{obj.key}', target.as_posix()

    if num_processes > 0:
        with multiprocessing.Pool(num_processes) as pool:
            pool.starmap(download_s3_file, generate_args())
    else:
        for args in generate_args():
            download_s3_file(*args)


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(3), retry=retry_if_exception_type(ClientError),
       reraise=True, after=log_after_first_attempt)
def upload_s3_file(local_path: str, s3_path: str) -> None:
    """Uploads the files from local_path to s3_path"""
    logger.info(f'Uploading {local_path} to {s3_path}')
    bucket, key = split_s3_path(s3_path)
    s3_client.upload_file(local_path, bucket, key)


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(3), retry=retry_if_exception_type(ClientError),
       reraise=True, after=log_after_first_attempt)
def delete_s3_file(s3_path: str) -> None:
    """Deletes the file from s3"""
    logger.info(f'Deleting {s3_path}')
    bucket, key = split_s3_path(s3_path)
    s3_client.delete_object(Bucket=bucket, Key=key)


def upload_to_s3(local_path: Union[str, Path], s3_path: str, num_processes: int = 8) -> None:
    """Uploads either a file or directory to s3"""
    local_path = Path(local_path)

    if local_path.is_file():
        return upload_s3_file(local_path.as_posix(), s3_path)

    bucket, key = split_s3_path(s3_path)

    def generate_args():
        for root, dirs, files in os.walk(local_path.as_posix()):

            for filename in files:
                # construct the full local path
                local_file = os.path.join(root, filename)

                # construct the full Dropbox path
                relative_path = os.path.relpath(local_file, local_path.as_posix())
                s3_file = os.path.join(key, relative_path)

                # relative_path = os.path.relpath(os.path.join(root, filename))
                yield local_file, f's3://{bucket}/{s3_file}'

    if num_processes > 0:
        with multiprocessing.Pool(num_processes) as pool:
            pool.starmap(upload_s3_file, generate_args())
    else:
        for args in generate_args():
            upload_s3_file(*args)


def s3_file_exists(s3_path: str) -> bool:
    """Check's if the file exists in a quick way"""
    bucket, key = split_s3_path(s3_path)
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False


def get_list_of_s3_files(remote_dir, list_of_file_extensions=None):
    files = []
    parts = urlparse(remote_dir, allow_fragments=False)
    bucket_name = parts.netloc
    search_prefix = parts.path.lstrip("/")
    bucket_obj = s3_resource.Bucket(bucket_name)

    for obj in bucket_obj.objects.filter(Prefix=search_prefix):
        if list_of_file_extensions and not obj.key.endswith(tuple(list_of_file_extensions)):
            continue
        files.append(os.path.join("s3://", bucket_name, obj.key))

    return files
