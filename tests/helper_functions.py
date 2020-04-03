import boto3
from botocore.exceptions import ClientError

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

