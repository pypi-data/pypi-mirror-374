# openapi_client.CommentApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_comment**](CommentApi.md#create_comment) | **POST** /v1/comments | 
[**create_reply**](CommentApi.md#create_reply) | **POST** /v1/designs/{designId}/comments/{threadId}/replies | 
[**create_reply_deprecated**](CommentApi.md#create_reply_deprecated) | **POST** /v1/comments/{commentId}/replies | 
[**create_thread**](CommentApi.md#create_thread) | **POST** /v1/designs/{designId}/comments | 
[**get_reply**](CommentApi.md#get_reply) | **GET** /v1/designs/{designId}/comments/{threadId}/replies/{replyId} | 
[**get_thread**](CommentApi.md#get_thread) | **GET** /v1/designs/{designId}/comments/{threadId} | 
[**list_replies**](CommentApi.md#list_replies) | **GET** /v1/designs/{designId}/comments/{threadId}/replies | 


# **create_comment**
> CreateCommentResponse create_comment(create_comment_request)

<Warning>

This API is deprecated, so you should use the [Create thread](https://www.canva.dev/docs/connect/api-reference/comments/create-thread/) API instead.

</Warning>

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Create a new top-level comment on a design.
For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/). A design can have a maximum
of 1000 comments.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_comment_request import CreateCommentRequest
from openapi_client.models.create_comment_response import CreateCommentResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    create_comment_request = openapi_client.CreateCommentRequest() # CreateCommentRequest | 

    try:
        api_response = api_instance.create_comment(create_comment_request)
        print("The response of CommentApi->create_comment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->create_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_comment_request** | [**CreateCommentRequest**](CreateCommentRequest.md)|  | 

### Return type

[**CreateCommentResponse**](CreateCommentResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_reply**
> CreateReplyV2Response create_reply(design_id, thread_id, create_reply_v2_request)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Creates a reply to a comment or suggestion thread on a design.
To reply to an existing thread, you must provide the ID of the thread
which is returned when a thread is created, or from the `thread_id` value
of an existing reply in the thread. Each thread can
have a maximum of 100 replies created for it.

For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_reply_v2_request import CreateReplyV2Request
from openapi_client.models.create_reply_v2_response import CreateReplyV2Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    design_id = 'design_id_example' # str | The design ID.
    thread_id = 'KeAbiEAjZEj' # str | The ID of the thread.
    create_reply_v2_request = openapi_client.CreateReplyV2Request() # CreateReplyV2Request | 

    try:
        api_response = api_instance.create_reply(design_id, thread_id, create_reply_v2_request)
        print("The response of CommentApi->create_reply:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->create_reply: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 
 **thread_id** | **str**| The ID of the thread. | 
 **create_reply_v2_request** | [**CreateReplyV2Request**](CreateReplyV2Request.md)|  | 

### Return type

[**CreateReplyV2Response**](CreateReplyV2Response.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_reply_deprecated**
> CreateReplyResponse create_reply_deprecated(comment_id, create_reply_request)

<Warning>

This API is deprecated, so you should use the [Create reply](https://www.canva.dev/docs/connect/api-reference/comments/create-reply/) API instead.

</Warning>

<Warning>

This API is currently provided as a preview. Be aware of the following:
- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Creates a reply to a comment in a design.
To reply to an existing thread of comments, you can use either the `id` of the parent
(original) comment, or the `thread_id` of a comment in the thread. Each comment can
have a maximum of 100 replies created for it.

For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_reply_request import CreateReplyRequest
from openapi_client.models.create_reply_response import CreateReplyResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    comment_id = 'KeAZEAjijEb' # str | The ID of the comment.
    create_reply_request = openapi_client.CreateReplyRequest() # CreateReplyRequest | 

    try:
        api_response = api_instance.create_reply_deprecated(comment_id, create_reply_request)
        print("The response of CommentApi->create_reply_deprecated:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->create_reply_deprecated: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **comment_id** | **str**| The ID of the comment. | 
 **create_reply_request** | [**CreateReplyRequest**](CreateReplyRequest.md)|  | 

### Return type

[**CreateReplyResponse**](CreateReplyResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_thread**
> CreateThreadResponse create_thread(design_id, create_thread_request)

<Warning>
This API is currently provided as a preview. Be aware of the following:
- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.
</Warning>

Creates a new comment thread on a design.
For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_thread_request import CreateThreadRequest
from openapi_client.models.create_thread_response import CreateThreadResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    design_id = 'design_id_example' # str | The design ID.
    create_thread_request = openapi_client.CreateThreadRequest() # CreateThreadRequest | 

    try:
        api_response = api_instance.create_thread(design_id, create_thread_request)
        print("The response of CommentApi->create_thread:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->create_thread: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 
 **create_thread_request** | [**CreateThreadRequest**](CreateThreadRequest.md)|  | 

### Return type

[**CreateThreadResponse**](CreateThreadResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_reply**
> GetReplyResponse get_reply(design_id, thread_id, reply_id)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Gets a reply to a comment or suggestion thread on a design.
For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_reply_response import GetReplyResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    design_id = 'design_id_example' # str | The design ID.
    thread_id = 'KeAbiEAjZEj' # str | The ID of the thread.
    reply_id = 'KeAZEAjijEb' # str | The ID of the reply.

    try:
        api_response = api_instance.get_reply(design_id, thread_id, reply_id)
        print("The response of CommentApi->get_reply:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->get_reply: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 
 **thread_id** | **str**| The ID of the thread. | 
 **reply_id** | **str**| The ID of the reply. | 

### Return type

[**GetReplyResponse**](GetReplyResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_thread**
> GetThreadResponse get_thread(design_id, thread_id)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Gets a comment or suggestion thread on a design.
To retrieve a reply to a comment thread, use the [Get reply](https://www.canva.dev/docs/connect/api-reference/comments/get-reply/) API.
For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_thread_response import GetThreadResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    design_id = 'design_id_example' # str | The design ID.
    thread_id = 'KeAbiEAjZEj' # str | The ID of the thread.

    try:
        api_response = api_instance.get_thread(design_id, thread_id)
        print("The response of CommentApi->get_thread:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->get_thread: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 
 **thread_id** | **str**| The ID of the thread. | 

### Return type

[**GetThreadResponse**](GetThreadResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_replies**
> ListRepliesResponse list_replies(design_id, thread_id, limit=limit, continuation=continuation)

<Warning>
This API is currently provided as a preview. Be aware of the following:
- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.
</Warning>

Retrieves a list of replies for a comment or suggestion thread on a design.

For information on comments and how they're used in the Canva UI, see the
[Canva Help Center](https://www.canva.com/help/comments/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.list_replies_response import ListRepliesResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.CommentApi(api_client)
    design_id = 'design_id_example' # str | The design ID.
    thread_id = 'KeAbiEAjZEj' # str | The ID of the thread.
    limit = 50 # int |  (optional) (default to 50)
    continuation = 'continuation_example' # str | If the success response contains a continuation token, the list contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example `?continuation={continuation}`.  To retrieve all items, you might need to make multiple requests. (optional)

    try:
        api_response = api_instance.list_replies(design_id, thread_id, limit=limit, continuation=continuation)
        print("The response of CommentApi->list_replies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommentApi->list_replies: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 
 **thread_id** | **str**| The ID of the thread. | 
 **limit** | **int**|  | [optional] [default to 50]
 **continuation** | **str**| If the success response contains a continuation token, the list contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example &#x60;?continuation&#x3D;{continuation}&#x60;.  To retrieve all items, you might need to make multiple requests. | [optional] 

### Return type

[**ListRepliesResponse**](ListRepliesResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

