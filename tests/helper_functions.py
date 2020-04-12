import json
import tempfile

import boto3

from botocore.exceptions import ClientError
from tests.variables_data import s3_bucket_ssm_param, s3_key


def update_parameter(parameter, value, param_type='String'):
    """
    Updates parameter to new value
    """
    ssm_client = boto3.client('ssm')
    response = ssm_client.put_parameter(
        Name=parameter,
        Value=value,
        Type=param_type,
        Overwrite=True,
        Tier='Standard'
        )
    return

def delete_parameters(parameters: list):
    ssm_client = boto3.client('ssm')
    response = ssm_client.delete_parameters(
        Names=parameters
    )
    return

def update_secret(name, value, secret_type='String'):
    """
    Updates secret to new value
    """
    
    secrets_client = boto3.client('secretsmanager')

    if secret_type == 'String':
        try:
            response = secrets_client.put_secret_value(
                SecretId=name,
                SecretString=value
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ResourceNotFoundException":
                response = secrets_client.create_secret(
                    Name=name,
                    SecretString=value
                )
    else:
        try:
            response = secrets_client.put_secret_value(
                SecretId=name,
                SecretBinary=value
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ResourceNotFoundException":
                response = secrets_client.create_secret(
                    Name=name,
                    SecretBinary=value
                )
    return

def get_s3_bucket_name():
    """
    Gets the name of the s3 bucket used for test
    """

    ssm_client = boto3.client('ssm')
    response = ssm_client.get_parameter(
        Name=s3_bucket_ssm_param
    )

    bucket_name = response['Parameter']['Value']
    return bucket_name

def upload_object(file_name, bucket_name, key):
    """
    upload file to s3
    """

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(file_name, bucket_name, key)

    return

def check_status_file(bucket_name, key):
    """
    Get content of file
    """

    s3 = boto3.client('s3')
    with tempfile.TemporaryFile() as data:
        s3.download_fileobj(bucket_name, s3_key, data)
        data.seek(0)
        status = json.loads(data.read().decode('utf-8'))['status']
    
    return status