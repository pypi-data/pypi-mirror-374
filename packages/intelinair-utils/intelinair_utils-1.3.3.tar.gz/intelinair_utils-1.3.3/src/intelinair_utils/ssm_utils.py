import json
from typing import Any

import boto3
from botocore.exceptions import ClientError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


@retry(wait=wait_exponential(multiplier=10, exp_base=1.5), stop=stop_after_attempt(5),
       retry=retry_if_exception_type(ClientError), reraise=True)
def get_parameter_from_ssm(parameter_name: str) -> Any:
    """
    Retrieve a parameter from SSM store.
    Args:
        parameter_name: the name of the parameter to retrieve

    Returns:
        the parameter value
    """
    ssm_client = boto3.client('ssm')
    parameter = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    return parameter['Parameter']['Value']


def get_json_parameter_from_ssm(parameter_name: str) -> Any:
    """
    Retrieve a parameter from SSM store and parse it as JSON.
    Args:
        parameter_name: the name of the parameter to retrieve

    Returns:
        parameter value

    """
    value = get_parameter_from_ssm(parameter_name)
    try:
        parsed_value = json.loads(value)
    except Exception as e:
        raise e
    else:
        return parsed_value
