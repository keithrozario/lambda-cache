import boto3

def update_parameter(parameter, value):
    """
    Updates parameter to new value
    """
    ssm_client = boto3.client('ssm')
    response = ssm_client.put_parameter(
        Name=parameter,
        Value=value,
        Type='String',
        Overwrite=True,
        Tier='Standard'
        )
    return

def update_secure_parameter(parameter, value):
    """
    Updates parameter to new value
    """
    ssm_client = boto3.client('ssm')
    response = ssm_client.put_parameter(
        Name=parameter,
        Value=value,
        Type='String',
        Overwrite=True,
        Tier='Standard'
        )
    return 