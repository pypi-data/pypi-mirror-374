"""
Provides a common API for working with remote storage services.

Currently this abstracts out both uploading and downloading of
files & folders from both SFTP and S3. Permissions for SFTP
access are stored within the class itself with for S3 the
credentials need to be exposed externally. See the `Boto3 docs`_
for how to configure this appropriately.

.. _`Boto3 docs`: http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuring-credentials

Example code::

   >>> Storage().download('sftp://Visual Data/', '.')
   >>> Storage().download('s3://flight-ops/VisualData/', '.')
"""

import ftplib
import logging
import os
import subprocess
import time
from abc import ABCMeta, abstractmethod
from typing import *
from urllib.parse import urlparse

import boto3

from intelinair_utils.storage_utils import get_files, path_split_all

logger = logging.getLogger("storage")


def get_backends() -> List[str]:
    """List available storage backends"""
    return list(storage_backends)


class Storage:
    """
    Primary class for working with remote files.

    The protocol backend is parsed out of the URL string and as such this class
    hides the protocol-specific implementations from the user.
    """

    def __init__(self) -> None:
        self.backends = {}  # type: Dict[str, StorageBackend]
        for n, backend in storage_backends.items():
            # Try to add all possible storage backends ignoring ones that
            # error.
            try:
                self.backends[n] = backend()
            except Exception as e:
                logger.warning("Failed to initialize storage backend '{}'" "".format(n))

    def _get_backend(self, url: str) -> "StorageBackend":
        """Returns if a URL is valid.

        Relies on a Backend for a given scheme to exist.
        """
        parsed_url = urlparse(url)
        if parsed_url.scheme not in storage_backends:
            raise ValueError("Scheme must be one of {}".format(list(storage_backends.keys())))
        else:
            return self.backends[parsed_url.scheme]

    def download(self, remote_url: str, local_path: Optional[str] = None, recursive: bool = False):
        """Download a file or the contents of a directory.

        If the remote_url is a directory, the contents of the directory will
        be downloaded into the specified local directory. If the remote_url is
        a file, it will be downloaded with the same filename into the
        specified local directory.
        """
        self._get_backend(remote_url).download(remote_url, local_path, recursive=recursive)

    def upload(self, local_path: str, remote_url: str):
        """Upload a file or the contents of a directory.

        If the local_path is a directory, the contents of the directory will
        be uploaded into the specified remote directory. If the local_path is
        a file, it will be uploaded with the same filename into the
        specified remote directory.
        """
        self._get_backend(remote_url).upload(local_path, remote_url)

    def remove(self, remote_url: str, recursive: bool = False):
        """Remove a file or the contents of a directory.

        If the remote_url is a directory, the contents of the directory will
        be removed recursively. If the remote_url is
        a file it will be removed from s3.
        """
        self._get_backend(remote_url).remove(remote_url, recursive=recursive)

    def exists(self, remote_url: str):
        """Checks if a remote url exists in S3."""
        return StorageBackendS3Cli().exists(remote_url)

    @staticmethod
    def exponential_backoff(function: Callable, *args):
        """
        Run a function using an exponential backoff during failure.

        Failure is defined here as the function raising any kind of exception.
        """
        tries = 3  # Number of times to attempt function()
        delay = 1  # Base amount of delay (seconds)
        backoff = 2  # Multiplier for determining delay after each failure
        for i in range(tries):
            try:
                return function(*args)
            except:
                logger.exception("Failed running function '{}', trying again after {}s.".format(function, delay))
                time.sleep(delay)
                delay *= backoff
        else:
            raise Exception("Failed to run '{}' {} times, aborting.".format(function, tries))


class StorageBackend(metaclass=ABCMeta):
    """Abstract class defining the interface for storage backends."""

    def __init__(self):
        pass

    @abstractmethod
    def download(self, remote_url: str, local_path: str, recursive: bool = False) -> None:
        pass

    @abstractmethod
    def upload(self, local_path: str, remote_url: str) -> None:
        pass

    @abstractmethod
    def remove(self, remote_url: str, recursive: bool = False) -> None:
        pass


class StorageBackendFtp(StorageBackend):
    """
    Implementation of an FTP backend for the Storage API.

    Assumes that explicit TLS is supported by the server (also known as FTPS).

    All login credentials are embedded in this library and no external
    configuration is necessary. Additionally this also means that only files on
    the IntelinAir FTP server can be accessed.
    """

    def __init__(self) -> None:
        self.ftp_uri = "ftp.intelinair.com"
        self.ftp_login = "bizdev@intelinair.com"
        self.ftp_pass = "FTP1simple"

    def _connect(self) -> None:
        # Log in to the FTP server and switch to a secure connection
        self.ftps = ftplib.FTP_TLS(self.ftp_uri)
        self.ftps.auth()
        self.ftps.login(self.ftp_login, self.ftp_pass)
        self.ftps.prot_p()

    def _disconnect(self) -> None:
        try:
            self.ftps.quit()
        except ftplib.all_errors as e:
            logger.exception("Exception during disconnect")

    def download(self, remote_uri: str, local_path: str, recursive: bool = False) -> None:
        """
        Fetches all files within the specified folder (relative to the root
        directory) from the IntelinAir FTP server and download to the specified
        directory. This replaces any content that was in that directory
        already.
        """
        assert recursive is False, "recursive downloading has not been tested for FTP"

        self._connect()

        # Find all the files in the desired directory
        self.ftps.cwd(remote_uri)
        files = self.ftps.nlst()
        logger.info('Found {} files in "{}"'.format(len(files), remote_uri))

        # Make sure the output directory exists
        try:
            os.makedirs(local_path)
        except FileExistsError:
            pass

        # And is empty
        # TODO

        # Copy all files to our local directory
        i = 1
        for filename in files:
            local_filename = os.path.join(local_path, filename)
            while True:
                try:
                    logger.info("{}/{} {} <- {}".format(i, len(files), local_filename, filename))

                    # Try to download the file
                    f = open(local_filename, "wb")
                    self.ftps.retrbinary("RETR {}".format(filename), f.write)
                    f.close()

                    # Verify file size of the downloaded file
                    filesize = int(self.ftps.sendcmd("SIZE {}".format(filename)).split(" ")[1])
                    stat = os.stat(local_filename)
                    if filesize != stat.st_size:
                        logger.error(
                            "Downloaded filesize ({}) doesn't match remote size ({}), retrying download.".format(
                                filesize, stat.st_size
                            )
                        )
                        os.remove(local_filename)
                        continue

                    # Stop retrying
                    break
                except ftplib.all_errors:
                    logger.exception("Failed to download '{}', trying again.".format(filename))

                    # Reconnect and go back to our data directory
                    self._disconnect()
                    self._connect()
                    self.ftps.cwd(remote_uri)
            i += 1

        self._disconnect()

    def upload(self, local_path: str, remote_uri: str) -> None:
        """
        Uploads all contents of the specified folder to the IntelinAir FTP
        server to the specified directory (remote_uri is assumed to be an
        absolute path even if the initial '/' is missing). This replaces any
        content that was in that directory already. Als all subfolder structure
        is preserved during uploading.
        """

        # Find all input files
        if os.path.isdir(local_path):
            files = get_files(local_path)
            logger.info("Found {} files in '{}'".format(len(files), local_path))
        elif os.path.isfile(local_path):
            logger.info("Found 1 file '{}'".format(local_path))
            files = [local_path]
            local_path = os.path.split(local_path)[0]
        else:
            raise Exception("ERROR: Non-file/non-directory path specified")

        # Make sure the remote_uri starts with a forward-slash
        if not remote_uri.startswith("/"):
            remote_uri = "/" + remote_uri

        # Make sure we're connected to the FTP server
        self._connect()

        # Copy all files to the remote directory
        i = 1
        for full_filename in files:
            filename = os.path.split(full_filename)[1]
            local_relpath = os.path.relpath(full_filename, local_path)
            remote_relpath = "/".join(path_split_all(local_relpath))

            dest_name = "/".join(
                [remote_uri, remote_relpath]
            )  # Don't use os.path because FTP server always uses '/' as directory separators
            logger.info("{}/{} {} -> {}".format(i, len(files), full_filename, dest_name))

            remote_folder = "/".join(dest_name.split("/")[:-1])
            self._mkdir(remote_folder)
            f = open(full_filename, "rb")
            self.ftps.storbinary("STOR {}".format(filename), f)
            f.close()
            i += 1

        self._disconnect()

    def _mkdir(self, path: str) -> None:
        """Create the given path on the FTP server"""
        dest_path = path.split("/")
        for i in range(0, len(dest_path)):
            curr_path = "/" + "/".join(dest_path[0: i + 1])
            try:
                self.ftps.cwd(curr_path)
            except ftplib.all_errors as e:
                response_code = str(e).split(" ")[0]
                if response_code == "550":
                    self.ftps.mkd(curr_path)
                    self.ftps.cwd(curr_path)
                    logger.debug("Making directory '{}'".format("/".join(dest_path[:i])))
                else:
                    logger.exception("Failed to set current working directory")

    def remove(self, remote_url: str, recursive: bool = False) -> None:
        pass


class StorageBackendS3Cli(StorageBackend):
    """
    Implementation of an Amazon S3 backend using aws cli for performance.

    This assumes that aws cli is installed and configured with the correct
    keys and default region.

    apt-get awscli

    aws configure
    key:
    code:
    default-region:us-east-1

    """

    def download(self, remote_url: str, local_path: str, recursive: bool = False):
        if local_path is None:
            local_path = "."

        # Split the path into the bucket name and the path within the bucket
        url = urlparse(remote_url)
        bucket_name = url.netloc
        if not bucket_name:
            raise ValueError("Missing bucket name in S3 URL")

        aws_cmd_string = 'aws s3 cp "' + remote_url + '" "' + local_path + '"'
        if recursive:
            aws_cmd_string = aws_cmd_string + " --recursive"

        retries_left = 5
        for _ in range(retries_left):
            logger.info("Running aws commandline like: {}".format(aws_cmd_string))
            # run aws command
            p = subprocess.Popen(aws_cmd_string, shell=True)
            if not p.wait():  # completed successfully
                break
            else:
                logger.warning("Download failed. Retries left : {}".format(retries_left))
                retries_left -= 1
        else:
            raise Exception(f"Failed to perform download operation")

    def upload(self, local_path: str, remote_url: str):
        if local_path is None:
            local_path = "."

        if not remote_url.endswith("/"):
            remote_url = remote_url + "/"

        # Split the path into the bucket name and the path within the bucket
        url = urlparse(remote_url)
        bucket_name = url.netloc
        if not bucket_name:
            raise ValueError("Missing bucket name in S3 URL")

        aws_cmd_string = 'aws s3 cp "' + local_path + '" "' + remote_url + '"'
        if os.path.isdir(local_path):
            aws_cmd_string = aws_cmd_string + " --recursive"

        retries_left = 5
        for _ in range(retries_left):
            logger.info("Running aws commandline like: {}".format(aws_cmd_string))

            # run aws command
            p = subprocess.Popen(aws_cmd_string, shell=True)
            if not p.wait():  # completed successfully
                break
            else:
                logger.warning("Upload failed. Retries left : {}".format(retries_left))
                retries_left -= 1
        else:
            raise Exception(f"Failed to perform upload operation")

    def remove(self, remote_url: str, recursive: bool = False):
        # Split the path into the bucket name and the path within the bucket
        url = urlparse(remote_url)
        bucket_name = url.netloc
        if not bucket_name:
            raise ValueError("Missing bucket name in S3 URL")

        if recursive and not remote_url.endswith("/"):
            # add "/" in the end
            remote_url = remote_url + "/"

        aws_cmd_string = 'aws s3 rm "' + remote_url + '"'
        if recursive:
            aws_cmd_string = aws_cmd_string + " --recursive"
        logger.info("Running aws commandline like: {}".format(aws_cmd_string))

        # run aws command
        p = subprocess.Popen(aws_cmd_string, shell=True)
        p.wait()
        return

    def exists(self, remote_url: str):
        self._connect()
        url = urlparse(remote_url)
        bucket_name, prefix = url.netloc, url.path.lstrip("/")
        if not bucket_name:
            raise ValueError("Missing bucket name in S3 URL")

        result = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        self._disconnect()
        return "Contents" in result

    def _connect(self) -> None:
        self.s3 = boto3.client("s3")

    def _disconnect(self) -> None:
        self.s3 = None


storage_backends = {"ftp": StorageBackendFtp, "s3": StorageBackendS3Cli}
