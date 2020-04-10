# Design Decision

## Where to store cached objects?

There's two possible locations to store cache objects within an execution context -- that will survive across invocations:

* The `/tmp` directory
* A `global` variable

Both aren't perfect, but between the two we chose `global` variables for two reasons:
* They exists only within the context of the application.
* They are faster than files on the file-system, as they don't require reading in or parsing out.

## Where to insert cached object?

We use a decorator construct to inject a cached object into the Lambda Context of the Lambda function. This is the simplest way to ensure the cache entry object is checked at every invocation. 

But where to insert the cache entry?

There's 4 options:

* Into Environment Variables of the Lamdba function
* Into the `event` dict of the Lambda function
* Into the `context` object of the Lambda function
* Into a newly created `cache` object of the Lambda function

[Middy](https://middy.js.org/docs/middlewares.html#ssm) by default uses environment variables, but provides an alternative for users to use the `context` instead. 

Environment variables make sense, and work. But, they're limited in their ability to store variables of type list of dictionaries and leaves a lot of work to the user to parse them as such. Additionally, as a matter of 'purity' these variables should be static for the lifetime of the execution context -- we are all practical, but environment variables are less easy to work with, hence we discard this option.

The `event` dictionary is a perfect place for the injecting the cache object. After all, it's the place your functions looks for most of it's data. But, the event object is dynamic in nature (depending on the trigger on your lambda), and we run the risk that a cache entry might over-write existing legitimate `event` data, causing hard to trouble-shoot issues.

Creating a new argument called cache, gives us a guarantee that the cache won't interfere with existing entries. like so:

```python
@secrets_manager.cache(secret_name)
def call_with_entry_name(event, context, cache):
    secret = cache.get(secret_name)
    return context
```
But this approach breaks the current norm of handlers accepting just two arguments (event and context). It looks like slightly less elegant, and might not be compatible with future python runtimes. 

Finally, the `context` object provides the following benefits:
* It already exists in the handlers arguments
* Its attributes and methods are fairly static. Risk of over-write is low.
* Variables here can take the form of any python type (str, int, list, dict...)

Because simplicity drives our design, the `context` object was chosen, as it provided the least friction for developers to use to the package, low risk of cache entry over-writing something, and it could natively handle any pythong type.

### Further Reading

* [AWS Lambda Context](https://docs.aws.amazon.com/lambda/latest/dg/python-context.html)
* [Reverse Engineering Lambda](https://www.denialof.services/lambda/)
* [bootstrap.py](https://gist.github.com/mshivaramie22/662eda1cbe63bf5716ffe5cc8a02811f)

