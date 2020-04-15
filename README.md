<h1 align="center"> lambda-cache </h1>
<h2 align="center"> Simple Caching for AWS Lambda</h2>

![PackageStatus](https://img.shields.io/static/v1?label=status&message=beta&color=blueviolet?style=flat-square) [![PyPI version](https://badge.fury.io/py/lambda-cache.svg)](https://badge.fury.io/py/lambda-cache) ![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.6%20|%203.7|%203.8&color=blue?style=flat-square&logo=python) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

![Test](https://github.com/keithrozario/lambda-cache/workflows/Test/badge.svg?branch=release) [![Coverage Status](https://coveralls.io/repos/github/keithrozario/lambda-cache/badge.svg?branch=release)](https://coveralls.io/github/keithrozario/lambda-cache?branch=release) [![Documentation Status](https://readthedocs.org/projects/simple-lambda-cache/badge/?version=latest)](https://simple-lambda-cache.readthedocs.io/en/latest/?badge=latest)

 [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 

# Introduction

![Screenshot](docs/images/lambda_cache.png)

_lambda-cache_ helps you cache data within your Lambda function **across** invocations. The package utilizes the internal memory of the lambda function's [execution context](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-context.html) to assist in caching, which in turn:

* Reduces load on back-end systems
* Reduces the execution time of the lambda
* Guarantees functions will reference latest data after caches have expired
* Reduces expensive network calls to APIs with throttling limits (or high charges)

_lambda-cache_ prioritizes simplicity over performance or flexibility. The goal is to provide the **simplest** way for developers to cache data across lambda invocations.

Currently supports SSM Parameters, Secrets Manager and S3 Objects.

# Installation

    $ pip install lambda-cache

Refer to [docs](https://lambda-cache.readthedocs.io/en/latest/) for how to include into your lambda function.

# Usage

```python
from lambda_cache import s3, ssm, secrets_manager


@ssm.cache(parameter='/prod/app/var')
@secrets_manager.cache(name='/prod/db/conn_string')
@s3.cache(s3Uri='s3://bucket_name/path/to/object.json')

def handler(event, context):
    var = getattr(context, 'var')
    secret = getattr(context, 'conn_string')
    with open("/tmp/object.json") as file_data:
        status = json.loads(file_data.read())['status']

    response = do_something(var,secret,status)

    return response
```

The first invocation of the function will populate the cache, after that all invocations over in the 60 seconds, will reference the parameter from the function's internal cache, without making a network calls to ssm, secrets manager or S3. After one minute, the the next invocation will refresh the cache from the respective back-ends.

Refer to [docs](https://lambda-cache.readthedocs.io/en/latest/user_guide/) for more info on how to change cache configurations.

# Credit

Project inspired by:
* [SSM-Cache](https://github.com/alexcasalboni/ssm-cache-python)
* [middy](https://github.com/middyjs/middy)
