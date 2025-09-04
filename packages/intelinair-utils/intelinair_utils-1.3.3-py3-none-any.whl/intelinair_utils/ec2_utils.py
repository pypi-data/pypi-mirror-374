"""Module contains various utility functions for AWS"""
import json
import logging
import subprocess
import sys
import time
from typing import Dict, List

import boto3
from botocore.exceptions import ClientError
import requests
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from intelinair_utils.retry_utils import log_after_first_attempt


__all__ = [
    "get_ec2_tags", "create_ec2_tags", "delete_ec2_tags", "ec2_is_spot",
    "get_ec2_meta", "shut_down", "make_aws_request", "get_ec2_spot_price",
    "get_ec2_ondemand_price"
]

logger = logging.getLogger("ec2_utils")


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8),
       reraise=True, after=log_after_first_attempt)
def get_ec2_tags(instance_id, region_name) -> Dict[str, str]:
    """Returns the EC2 tags for this instance."""

    ec2 = boto3.resource('ec2', region_name=region_name)
    i = ec2.Instance(id=instance_id)
    tags = dict([(i['Key'], i['Value']) for i in i.tags])

    return tags


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8),
       reraise=True, after=log_after_first_attempt)
def create_ec2_tags(instance_id: str, tags: List[Dict[str, str]], region_name: str) -> None:
    ec2 = boto3.resource("ec2", region_name=region_name)
    ec2.create_tags(
        Resources=[instance_id],
        Tags=tags
    )


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8),
       reraise=True, after=log_after_first_attempt)
def delete_ec2_tags(instance_id, region_name, tags) -> None:
    client = boto3.client("ec2", region_name=region_name)
    client.delete_tags(Resources=[instance_id], Tags=[{"Key": tag} for tag in tags])


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8),
       reraise=True, after=log_after_first_attempt)
def ec2_is_spot(instance_id, region_name) -> bool:
    ec2 = boto3.resource('ec2', region_name=region_name)
    instance = ec2.Instance(id=instance_id)

    return True if instance.spot_instance_request_id is not None else False


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8),
       reraise=True, after=log_after_first_attempt)
def get_ec2_meta() -> Dict[str, str]:
    # Get the instance ID and availability zone for this instance
    instance_id = requests.get(
        "http://169.254.169.254/latest/meta-data/instance-id", timeout=10).text
    logger.debug(f"AWS EC2 Instance ID: {instance_id}")
    availability_zone = requests.get(
        "http://169.254.169.254/latest/meta-data/placement/availability-zone", timeout=10).text
    logger.debug(f"AWS EC2 Availability Zone: {availability_zone}")
    instance_type = requests.get("http://169.254.169.254/latest/meta-data/instance-type", timeout=10).text
    logger.debug(f"AWS EC2 instance type: {instance_type}")
    meta = {
        "instance_id": instance_id,
        "instance_type": instance_type,
        "availability_zone": availability_zone
    }

    # Map from the availability zone to a region name
    try:
        int(availability_zone.split("-")[-1])
        region_name = availability_zone
    except ValueError:
        region_name = availability_zone[:-1]
    meta["region"] = region_name
    logger.debug(f"AWS EC2 Region: {region_name}")

    return meta


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8),
       reraise=True, after=log_after_first_attempt)
def shut_down(in_ec2: bool = True) -> None:
    """Shut downs ec2 instance."""
    if in_ec2:
        # Power-off the server
        subprocess.run("sudo poweroff", shell=True)
    else:
        # this is local run, just exit
        sys.exit(1)


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8), retry=retry_if_exception_type(ClientError),
       reraise=True, after=log_after_first_attempt)
def make_aws_request(function_name, kwargs, region_name=None):
    response = None
    if not region_name:
        region_name = boto3.DEFAULT_SESSION.region_name
    response = function_name(**kwargs)

    return response


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8), retry=retry_if_exception_type(ClientError),
       reraise=True, after=log_after_first_attempt)
def get_ec2_spot_price(instance_type, availability_zone, operating_system):
    """Get EC2 instance spot price"""
    client = boto3.client('ec2')
    response = client.describe_spot_price_history(
        Filters=[{'Name': 'product-description', 'Values': [operating_system]}],
        AvailabilityZone=availability_zone,
        StartTime=time.time(),
        EndTime=time.time(),
        InstanceTypes=[instance_type])

    if len(response['SpotPriceHistory']) > 0:
        return float(response['SpotPriceHistory'][0]['SpotPrice'])
    else:
        return None


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(8), retry=retry_if_exception_type(ClientError),
       reraise=True, after=log_after_first_attempt)
def get_ec2_ondemand_price(instance_type, region, operating_system="Linux"):
    """
    Gets EC2 on-demand price based on provided parameters:
    "licenseModel": Checks to see if the target EC2 Instance price is for Bring your own license ,
    "preInstalledSw": This is for EC2 Instances that uses an EC2 Image (AMI) that has a preinstalled SQL Server.
    """
    client = boto3.client('pricing')
    response = client.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {"Type": "TERM_MATCH", "Field": "regionCode", "Value": f"{region}"},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": f"{operating_system}"},
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": f"{instance_type}"},
            {"Type": "TERM_MATCH", "Field": "marketoption", "Value": "OnDemand"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "licenseModel", "Value": "No License required"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"}
        ]
    )

    if len(response['PriceList']) > 0:
        price = json.loads(response['PriceList'][0])
        for on_demand in price['terms']['OnDemand'].values():
            for price_dimensions in on_demand['priceDimensions'].values():
                price_value = price_dimensions['pricePerUnit']['USD']
                return float(price_value)
    else:
        return None
