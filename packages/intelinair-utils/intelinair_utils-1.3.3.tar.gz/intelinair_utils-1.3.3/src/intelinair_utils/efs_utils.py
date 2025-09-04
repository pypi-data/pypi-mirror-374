import json
import logging
import os
from typing import List, Union

import boto3

from intelinair_utils.os_utils import call_command

__all__ = ["attach_available_efses", "get_available_efses", "get_available_efses_from_s3", "get_efs_ip_address"]

logger = logging.getLogger(__name__)


def get_available_efses(
    env: str,
    efs_client: boto3.client,
    ec2_client: boto3.client,
    availability_zone: str
) -> Union[List, None]:
    """Find available efses based on environment

    Args:
        env (str): Environment of a machine
        efs_client (boto3.client): boto3 efs client
        ec2_client (boto3.client): boto3 ec2 client
        availability_zone (str): availability zone id

    Returns:
        Union[List, None]: Available efses, list of dicts with efs info
                            {
                                "id": "fs-id",
                                "name": "efs-name",
                                "ip_address": "ip-address",
                                "az": "availability-zone"
                            }
    """
    efs_to_attach = []
    efs_filesystems = efs_client.describe_file_systems()
    zone_id = ec2_client.describe_availability_zones(ZoneNames=[availability_zone])[
        "AvailabilityZones"][0]['ZoneId']
    for efs_filesystem in efs_filesystems['FileSystems']:
        efs_tags = parse_aws_tags(efs_filesystem['Tags'])
        if efs_tags.get('Environment', {}) == env and efs_tags.get('Service', {}) == 'pipeline':
            efs = {}
            efs['id'] = efs_filesystem['FileSystemId']
            efs['name'] = efs_filesystem['Name']
            ip_address = get_efs_ip_address(efs['id'], zone_id, efs_client, ec2_client)
            efs['ip_address'] = ip_address
            efs['az'] = availability_zone
            efs_to_attach.append(efs)
            break

    return efs_to_attach


def parse_aws_tags(tags: list) -> dict:
    """
    Simple method to parse AWS tags from list to dict.
    Args:
        tags: list of dicts of AWS object.
    Returns:
        tags in standard key value representation.
    """
    return {tag['Key']: tag['Value'] for tag in tags}


def get_available_efses_from_s3(s3_client: boto3.client, env: str, availability_zone: str):
    bucket = 'intelinair-infra'
    key = f'pipeline-metadata/efs/{env}/efs.json'
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    efses = json.loads(obj['Body'].read().decode('utf-8'))

    efs_to_attach = []

    for efs in efses:
        if efs['az'] == availability_zone:
            efs_to_attach.append(efs)
    return efs_to_attach


def get_efs_ip_address(
    efs_id: str,
    zone_id: str,
    efs_client: boto3.client,
    ec2_client: boto3.client
) -> Union[ str, None]:
    """Finds ip address of efs based on efs id and availability zone id

    Args:
        efs_id (str): efs_id
        zone_id (str): availability zone id
        efs_client (boto3.client): boto3 efs client
        ec2_client (boto3.client): boto3 ec2 client

    Returns:
        str: The ip address of efs in the availability zone
    """

    ip_address = None
    mount_targets = efs_client.describe_mount_targets(FileSystemId=efs_id)['MountTargets']
    for mount_target in mount_targets:
        subnet_id = mount_target['SubnetId']
        subnets = ec2_client.describe_subnets(SubnetIds=[subnet_id])
        az_id = subnets['Subnets'][0]['AvailabilityZoneId']
        if az_id == zone_id:
            ip_address = mount_target['IpAddress']
            break
    return ip_address


def attach_available_efses(env: str, region: str, availability_zone: str) -> Union[List, None]:
    """Attaches available efses based on environment
       Filters efses based on env tag and attaches.

    Args:
        env (str): Environment of a machine
        region (str): Machine region
        availability_zone (str): Region's availability zone

    Returns:
        Union[List, None]: None in case of failure or List of attached efses
    """

    # if EFS isn't from prod than it's from dev
    if env != "prod":
        env = "dev"

    mount_points = []
    s3_client = boto3.client('s3')
    efs_to_attach = get_available_efses_from_s3(s3_client, env, availability_zone)

    for efs in efs_to_attach:
        mount_point = os.path.join("/mnt", efs['name'])

        if not os.path.exists(mount_point):
            os.system(f"sudo mkdir -p {mount_point}")

        # handling from different vpc case
        ip_address = efs['ip_address']
        cmd = f'echo "{ip_address} {efs["id"]}.efs.{region}.amazonaws.com" | sudo tee -a /etc/hosts'
        ret_code, error_txt, stderr = call_command(cmd, 'mount_efs', silent=True)
        if ret_code != 0:
            logger.error(stderr)
            return

        # mount efs
        cmd = f"sudo mount -t efs {efs['id']}:/ {mount_point}"
        ret_code, error_txt, stderr = call_command(cmd, 'mount_efs', silent=True)
        if ret_code != 0:
            logger.error(stderr)
            return
        os.system(f"sudo chown $USER:$USER {mount_point}")
        mount_points.append(mount_point)

    return mount_points
