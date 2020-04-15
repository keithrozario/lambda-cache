# lambda-cache

Simple caching for AWS Lambda.

The goal of the package is to provide a simple interface for caching, built specifically for AWS Lambda.

## Simple use-case

Our goal is to enable Lambda functions to cache data internally for a period of time, without incurring the delay of making a large number of network calls:

![Screenshot](images/lambda_cache.png)

To do so via code, we decorate our handler method with the `ssm.cache` function:

```python
from lambda_cache import ssm

@ssm.cache(parameter='/production/app/var')
def handler(event, context):
    var = getattr(context, 'var')
    response = do_something(var)
    return response
```

All invocations after the first, will reference the parameter from the function's internal cache, without making a network call to ssm (which incurs a ~50ms delay). After 60 seconds has lapsed, the next invocation will get the latest value from SSM. 

This increases the functions performance, reduces the load on back-end services, and guarantees that invocations after a set-time will begin using the latest parameter value. 

## Caching Basics

When a Lambda function is invoked, AWS Lambda launches a temporary environment called an [execution context](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-context.html), that initializes the function's runtime and code. After the function has executed, AWS Lambda maintains the execution context for some time in anticipation of another invocation.

This 'warm' execution context _might_ be reused for the next invocation, as it is more efficient than creating a new execution context for every invocation. Re-using an execution context will keep the following:

* All Objects declared outside the function's handler method.
* Any file within the `/tmp` directory
* Background processes and callbacks initiated by Lambda that did not complete.

AWS provide no guarantees on how long execution contexts are kept warm before they are discarded. It probably depends on the load on the service at the time. Applicationshave no control over re-using or getting new execution contexts, it is left to AWS.

Given that, there are only two options to keep an object in the functions memory, across multiple invocations of that same function.

**Option 1**: Lookup the object outside the function's handler. This method is fast, cheap and causes the least load on back-end services like SSM or Databases. But because we cannot guarantee how long execution contexts are kept warm, an update to an object, for example a parameter in SSM Parameter store might take hours before they effect function invocations (when all warm functions are finally discarded)

**Option 2**: Lookup the object on every invocation. This method is slow, expensive, and causes high load on backend systems. But it guarantees that an update to an object takes effect immediately.

_lambda_cache_ provides a 3rd option, by looking up the object at specific frequencies (e.g. once every hour). Thereby still being fast and cheap, but also guarantee that and update will take effect within a set time across all lambda invocations.

## Why use lambda_cache

The philosophy around _lambda_cache_ is to provide a simple interface for developers to start caching within their Lambda functions, with minimal tweaking necessary. Some call it 'opioniated', we call it simple. 








