import json
import boto3
import os

from lambda_cache import s3
from variables_data import s3_bucket_ssm_param, s3_key

def generic_return(message):
    body = {
        "message": message
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response


@s3.cache(s3Uri=f"s3://{os.environ['S3_BUCKET']}/{s3_key}", entry_name='temp_key.json', max_age_in_seconds=5, check_before_download=False)
def s3_download(event, context):
    with open("/tmp/temp_key.json") as file_data:
        status = json.loads(file_data.read())['status']

    return generic_return(status)