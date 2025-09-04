"""Authorization token storage and retrieval classes for AgMRI API
"""
import json
import logging
import os.path
import string
from collections import namedtuple

import boto3
import botocore.exceptions
import filelock

logger = logging.getLogger(__name__)

__all__ = ['SSMStore', 'FileStore', 'TokenPair']

PROCESSING_TOKENS_TEMPLATE = "/global/processing/tokens/{environment}/{username}/{token_type}"

"""Authorization tokens stored together

Attributes:
    access_token: JWT access token with a short lifetime
    refresh_token: Refresh token with a long lifetime that can
                   be used to get a new access token
"""
TokenPair = namedtuple('TokenPair', ['access_token', 'refresh_token'])


class SSMStore:
    """Store and retrieve tokens from the AWS SSM Parameter Store
    """

    def __init__(self, environment, username):
        self.environment = environment
        self.username = self.clean_username(username)

    @staticmethod
    def clean_username(username):
        """Remove all non-alphanumeric characters from the username

        Args:
            username: the username (usually an email) to clean

        Returns:
            the cleaned username
        """
        return ''.join([c if c in string.ascii_letters + string.digits else '_' for c in username])

    def get_tokens(self) -> TokenPair:
        """Retrieve the tokens from the parameter store
        """
        # Not defining as a property as ssm client is not picklable which is an issue for cropping metaflow pipeline
        ssm = boto3.client('ssm')
        token_dict = {}
        for token_type in TokenPair._fields:
            name = PROCESSING_TOKENS_TEMPLATE.format(environment=self.environment,
                                                     username=self.username,
                                                     token_type=token_type)
            parameter = ssm.get_parameter(Name=name, WithDecryption=True)
            token_dict[token_type] = parameter['Parameter']['Value']
        return TokenPair(**token_dict)

    def _store_token(self, token_type: str, token_value: str):
        """Store a token in the parameter store

        Args:
            token_type: the type of token to store
            token_value: the value of the token
        """
        # Not defining as a property as ssm client is not picklable which is an issue for cropping metaflow pipeline
        ssm = boto3.client('ssm')
        try:
            name = PROCESSING_TOKENS_TEMPLATE.format(environment=self.environment,
                                                     username=self.username,
                                                     token_type=token_type)
            ssm.put_parameter(
                Name=name,
                Value=token_value,
                Type='SecureString',
                Overwrite=True
            )
        except botocore.exceptions.ClientError as exc:
            # Boto3 classifies all AWS service errors and exceptions as ClientError exceptions
            logger.warning(
                f"Failed to store token to the parameter store with exception {exc.response['Error']['Code']}"
            )

    def store_tokens(self, tokens: TokenPair):
        """Store the tokens in the parameter store

        Args:
            tokens: the tokens to store
        """
        for token_type, token_value in tokens._asdict().items():
            self._store_token(token_type, token_value)


class FileStore:
    """Store and retrieve tokens from a local file
    """

    def __init__(self, environment, username, path=None):
        self.environment = environment
        self.username = username
        self.token_path = path if path is not None else os.path.expanduser(f'~/.agmri.{environment}.tokens')
        self.token_lock_path = self.token_path + '.lock'

    def get_tokens(self):
        """Retrieve the tokens from the file
        """
        with filelock.FileLock(self.token_lock_path):
            with open(self.token_path, 'r', encoding='utf-8') as tokens_file:
                tokens_json = json.load(tokens_file)
                return TokenPair(**tokens_json)

    def store_tokens(self, tokens: TokenPair):
        """Store the tokens in the file

        Args:
            tokens: the tokens to store
        """
        with filelock.FileLock(self.token_lock_path):
            with open(self.token_path, 'w', encoding='utf-8') as tokens_file:
                json.dump(tokens._asdict(), tokens_file)
