import base64
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

import boto3
import docker
import docker.errors
from docker.models.containers import Container
from requests import ReadTimeout
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_result
from intelinair_utils.logging_utils import set_standard_logging_config

set_standard_logging_config()
logger = logging.getLogger('docker_utils')


region_name = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
docker_client = docker.from_env(timeout=300)
docker_auth = None
pulled_images = list()
retryable_errors = ('sqlite3.OperationalError',)


class ErrorLoggerException(Exception):

    def __init__(self, exit_code: int = None, message: str = None):
        super().__init__()
        self.exit_code = exit_code
        self.message = message

    def __str__(self):
        return f'ErrorLoggerException(exit_code={self.exit_code}, message={self.message})'

    def __eq__(self, other: 'ErrorLoggerException'):
        if self.exit_code == other.exit_code and self.message == other.message:
            return True
        return False


class DockerStageException(Exception):

    def __init__(self, exit_code: int = None, message: str = None):
        super().__init__()
        self.exit_code = exit_code
        self.message = message

    def __str__(self):
        return f'DockerStageException(exit_code={self.exit_code}, message={self.message})'

    def __eq__(self, other: 'DockerStageException'):
        if self.exit_code == other.exit_code and self.message == other.message:
            return True
        return False


@retry(wait=wait_exponential(multiplier=2), stop=stop_after_attempt(3), reraise=True)
def get_aws_credentials():
    """Returns frozen aws credentials given the current credentials chain"""
    session = boto3.Session()
    return session.get_credentials().get_frozen_credentials()


def get_docker_auth() -> Dict:
    """Returns the username and password for using ECR."""
    ecr = boto3.client('ecr')
    auth_creds = ecr.get_authorization_token()['authorizationData'][0]
    username, password = base64.b64decode(auth_creds['authorizationToken']).decode('utf-8').split(':')
    return {
        'username': username,
        'password': password
    }


def remove_old_docker_images(repo: str, tag: str):
    """
    Remove old images of the same repo if exist
    Args:
        repo: image repository name
        tag: image tag
    """
    docker_images = docker_client.images.list(name=repo)
    for docker_image in docker_images:
        for _tag in docker_image.tags:
            if not _tag.endswith(tag):
                logger.info(f"Removing older image version {_tag}")
                docker_client.images.remove(docker_image.id, force=True)


def _log_pull_generator(pull_logs: List, log_period_seconds: int = 30):
    """Generator for pull logs"""
    t = time.time()
    last_log = ""
    for log in pull_logs:
        last_log = log
        if time.time() - t > log_period_seconds:
            t = time.time()
            logger.info(last_log)
    if last_log:
        logger.info(last_log)


def pull_docker_image(image: str) -> Union[None, str]:
    """Ensures the image is pulled locally

    Args:
        image: the docker image to pull

    Returns:
        an error message upon failure otherwise None
    """
    global docker_auth, pulled_images
    try:
        if ':' in image:
            repo, tag = image.split(':')
        else:
            repo, tag = image, 'latest'
    except Exception as e:
        logger.error('Failed to parse docker image tag')
        logger.exception(e, exc_info=True)
        raise e

    if (repo, tag) in pulled_images:
        return

    if os.environ.get('IN_EC2') == 'YES':
        for _ in range(3):
            try:
                remove_old_docker_images(repo, tag)
            except docker.errors.APIError:
                logger.error("Failed to remove older image version. Retrying")
                time.sleep(30)
            else:
                break
        else:
            logger.error(f"Failed to remove older image versions for {repo}")

    try:
        logger.info(f'Pulling docker image = {repo}:{tag}')
        pull_logs = docker_client.api.pull(repo, tag=tag, auth_config=docker_auth, stream=True, decode=True)
        _log_pull_generator(pull_logs)
        logger.info("Docker is successfully pulled")
    except docker.errors.APIError:
        logger.info('Failed to pull image, attempting to get new credentials')
        docker_auth = get_docker_auth()
        logger.info('Successfully got credentials')
        try:
            pull_logs = docker_client.api.pull(repo, tag=tag, auth_config=docker_auth, stream=True, decode=True)
            _log_pull_generator(pull_logs)
            logger.info("Docker is successfully pulled")
        except docker.errors.APIError as e:
            logger.error('Failed to pull docker image')
            logger.exception(e, exc_info=True)
            raise e
    finally:
        pulled_images.append((repo, tag))


def check_source_volumes_exist(volumes: Optional[List[str]]):
    """Function that checks whether given list of volumes exist."""
    if not volumes:
        return
    for v in volumes:
        source_volume, _ = v.split(':')
        source_path = Path(source_volume).expanduser()
        if not source_path.exists():
            logger.info(f'Creating source volume directory {source_path}')
            source_path.mkdir(parents=True, mode=0o777)


def is_retryable_return_value(exception):
    if isinstance(exception, DockerStageException):
        for retryable_error in retryable_errors:
            if retryable_error in exception.message:
                return True
        raise exception
    return False


@retry(
    retry=retry_if_result(is_retryable_return_value)
)
def call_docker(
        image: str,
        python_script_path: str,
        command_name: str = '',
        runtime: str = None,
        script_args: list = None,
        script_kwargs: dict = None,
        shared_memory: str = None,
        user: str = 'ubuntu',
        group: str = 'ubuntu',
        working_dir: str = None,
        volumes: List[str] = None,
        environment: Dict = None,
        max_runtime: int = 60 * 5,
        pipeline_version: Optional[str] = None,
) -> None:
    """Starts the script in the image with the specified kwargs

    Args:
        image: The docker image to pull and use
        python_script_path: the python script to run inside the image
        command_name: docker command name
        runtime: the container runtime to use
        script_args: a list of args to pass to the script
        script_kwargs: the kwargs to pass to the script, will pass like --{key} {value} for each item
        shared_memory: the amount of shared memory to pass to the container
        user: the user to run the docker container as
        group: the group to run the docker container in
        working_dir: the directory to use as the working dir inside the container
        volumes: A list of volumes to mount
        environment: a dictionary of extra environment variables for the container
        max_runtime: the max number of seconds to wait for the container to finish
        pipeline_version: the version of the pipeline to run the container if function is used in image processing.

    Returns:
        an error message upon failure or None otherwise
    """
    ret_code = None
    error_msg = f'Failed to process docker command {command_name}'

    try:
        pull_docker_image(image=image)
        check_source_volumes_exist(volumes)
        ret_code, error_msg, from_error_logger = run_container(
            image=image,
            script_args=script_args,
            script_kwargs=script_kwargs,
            python_script_path=python_script_path,
            runtime=runtime,
            volumes=volumes,
            shared_memory=shared_memory,
            user=user,
            group=group,
            working_dir=working_dir,
            environment=environment,
            max_runtime=max_runtime,
            pipeline_version=pipeline_version
        )

    except (TimeoutError, MemoryError, ReadTimeout) as e:
        logger.warning("Attempting a rerun on a larger machine.")
        logger.warning(e)
        logger.warning(e.__class__)
        raise MemoryError()

    except Exception as e:
        logger.error(error_msg)
        logger.exception(e)
        if ret_code is not None and ret_code != 0:
            error_msg = f"{error_msg}, Return code: {ret_code}"
        raise Exception(error_msg)
    else:
        if ret_code != 0 and from_error_logger:
            raise ErrorLoggerException(exit_code=ret_code, message=error_msg)
        elif ret_code != 0:
            raise DockerStageException(exit_code=ret_code, message=error_msg)


# Debug utility
def build_docker_command(image: str,
                         command: str,
                         shm_size: str,
                         user: str,
                         volumes: List,
                         environment: Dict,
                         **kwargs: Dict):
    """Builds a docker command from the given parameters"""
    docker_command = f'docker run --rm --net host --shm-size={shm_size} --user {user} '
    docker_command += ' '.join([f'-v {v}' for v in volumes]) + ' '
    docker_command += ' '.join(f'--env "{k}={environment[k]}" ' for k in environment) + ' '
    docker_command += f' {image} ' + ' '.join(command)
    return docker_command


def run_container(
        image: str,
        user: str,
        group: str,
        python_script_path: str,
        runtime: str,
        script_args: List,
        script_kwargs: Dict,
        shared_memory: str,
        working_dir: str,
        volumes: List[str],
        environment: Dict,
        max_runtime: int,
        pipeline_version: Optional[str] = None,
) -> Tuple:
    """Starts the script in the image with the specified kwargs

    Args:
        image: The docker image to pull and use
        python_script_path: the python script to run inside the image
        runtime: the docker runtime to execute with (eg nvidia)
        script_args: a list of args to pass to the script
        script_kwargs: the kwargs to pass to the script, will pass like --{key} {value} for each item
        shared_memory: the amount of shared memory to pass to the container
        user: the user to run the docker container as
        group: the group to run the docker container as
        working_dir: the directory to use as the working directory inside the container
        volumes: A list of volumes to mount
        environment: a dictionary of extra environment variables for the container
        max_runtime: the max number of seconds to wait for the container to finish
        pipeline_version: the version of the pipeline to run the container if function is used in image processing.

    Returns:
        an error message upon failure or None otherwise
    """

    credentials = get_aws_credentials()

    final_script_args = list()

    if script_args:
        final_script_args.extend(script_args)

    if script_kwargs:
        for k in script_kwargs:
            final_script_args.extend([f'--{k}', script_kwargs[k]])

    run_kwargs = {
        'image': image,
        'command': [str(a) for a in ['python3', python_script_path] + final_script_args],
        'runtime': runtime,
        'shm_size': shared_memory,
        'user': user,
        'group_add': [group],
        'network': 'host',
        'volumes': volumes,
        'working_dir': working_dir,
        'environment': {
            'AWS_DEFAULT_REGION': region_name,
            'AWS_ACCESS_KEY_ID': credentials.access_key,
            'AWS_SECRET_ACCESS_KEY': credentials.secret_key,
            'AWS_SESSION_TOKEN': credentials.token if credentials.token else '',
            # set ENV variable  IA_LOGGING_FMT
            # getting root logger's handler formatter
            'IA_LOGGING_FMT': logging.getLogger().handlers[0].formatter._fmt,
            'IA_DOCKER_IMAGE': image,
        },
        'detach': True
    }
    if pipeline_version is not None:
        run_kwargs['environment']['IA_PIPELINE_VERSION'] = pipeline_version

    if environment:
        run_kwargs['environment'].update(environment)

    # set a breakpoint here to get a docker command you can test in isolation
    # debug_command = self.build_docker_command(**run_kwargs)
    container = docker_client.containers.run(**run_kwargs)
    return log_and_shutdown_container(container=container, max_runtime=max_runtime,
                                      output_dir=script_kwargs.get('output_dir'))


def log_and_shutdown_container(container: Container, max_runtime: int, output_dir: str = None) -> Tuple[int, str, bool]:
    """Logs the container and shut it down."""
    logs = []
    for attempt in range(max_runtime):
        time.sleep(1)
        container.reload()
        logs = container.logs(stream=True, follow=False)
        if not container.attrs['State']['Running']:
            break

    else:
        logger.error(f"The container with image {container.image} could "
                       f"not finish the job in {max_runtime} seconds >> LOGS:")

        for log in logs:
            decoded_log = log.decode('utf-8').strip('\n')
            logger.warning(decoded_log, extra={'simple': True})
        raise TimeoutError()

    decoded_logs = []
    logs = dict.fromkeys(logs)
    for log in logs:
        # if logging receives 'simple' kwarg,
        # it disables current format and logs as is.

        decoded_log = log.decode('utf-8').strip('\n')
        logger.info(decoded_log, extra={'simple': True})
        decoded_logs.append(decoded_log)

    logger.info(f'Container status: {container.status}')
    exit_result = container.wait()
    ret_code = exit_result['StatusCode']
    logger.info(f'Container exit code: {ret_code}')

    container.remove()
    error_message = None
    error_file_exists = os.path.exists(os.path.join(output_dir, 'error.txt')) if output_dir else False
    if ret_code in (137, 247):  # Killed for using too much memory
        logger.warning(f"Container returned exit code {ret_code}")
        raise MemoryError()
    elif ret_code != 0 and error_file_exists:
        try:
            with open(os.path.join(output_dir, 'error.txt'), 'r') as fp:
                error_message = fp.read().split('\n')[1].strip()
        except Exception as e:
            logger.error(repr(e))
            logger.warning(f"Could not retrieve error message from error logger.")

    elif ret_code != 0 and not error_file_exists:
        # In case of failure the last block of errors logged streamed from inside
        # the container is printed along with the stats log for easier debugging.
        try:
            error_message = get_last_traceback(decoded_logs=decoded_logs)
        except Exception as e:
            logger.error(repr(e))
            logger.warning(f"Could not retrieve the last logs of the job, that failed inside the container.")

    return ret_code, error_message, error_file_exists


def get_last_traceback(decoded_logs: List[str]) -> str:
    """
    Args:
        decoded_logs: The list of logs streamed in docker

    Returns:
        EITHER The last block of logs beginning from 'Traceback' formatted
        in the blank OR the full logs (when no 'Traceback' line was found).
    """
    inverted_error_logs = decoded_logs[::-1]  # starting from end
    is_short = lambda ll, i: len(ll) < i + 1  # recursion safe exit
    is_traceback = lambda elem: 'Traceback' in elem

    # getting the last block
    get_last = lambda ll, i: ll[:i + 1] if is_short(ll, i) or is_traceback(ll[i]) else get_last(ll, i + 1)

    traceback_block_as_list = get_last(inverted_error_logs, 0)
    traceback_block = "\n".join(traceback_block_as_list[::-1])  # re-inverted

    return f"{traceback_block}"
