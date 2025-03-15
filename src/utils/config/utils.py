import logging
import boto3
from botocore.exceptions import ClientError


def get_log_level(level_str):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return levels.get(level_str.upper(), logging.ERROR)



def get_ssm_parameter(name, region_name = "eu-west-1", decription = True):
    ssm = boto3.client('ssm', region_name=region_name)
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=decription)
        return response['Parameter']['Value']
    except ClientError as e:
        print(f"Error retrieving parameter: {e}")
        return None


