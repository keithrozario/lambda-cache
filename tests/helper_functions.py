import boto3

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