# openapi_client.ResizeApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_design_resize_job**](ResizeApi.md#create_design_resize_job) | **POST** /v1/resizes | 
[**get_design_resize_job**](ResizeApi.md#get_design_resize_job) | **GET** /v1/resizes/{jobId} | 


# **create_design_resize_job**
> CreateDesignResizeJobResponse create_design_resize_job(create_design_resize_job_request=create_design_resize_job_request)

<Note>

To use this API, your integration must act on behalf of a user that's on a Canva plan with premium features (such as Canva Pro).

</Note>

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints)
to create a resized copy of a design. The new resized design is
added to the top level of the user's
[projects](https://www.canva.com/help/find-designs-and-folders/) (`root` folder).

To resize a design into a new design, you can either:

  - Use a preset design type.
  - Set height and width dimensions for a custom design.

Note the following behaviors and restrictions when resizing designs:
- Designs can be resized to a maximum area of 25,000,000 pixels squared.
- Resizing designs using the Connect API always creates a new design. In-place resizing is currently not available in the Connect API, but can be done in the Canva UI.
- Resizing a multi-page design results in all pages of the design being resized. Resizing a section of a design is only available in the Canva UI.
- [Canva docs](https://www.canva.com/create/documents/) can't be resized, and other design types can't be resized to a Canva doc.
- Canva Code designs can't be resized, and other design types can't be resized to a Canva Code design.

<Note>
For more information on the workflow for using asynchronous jobs,
see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).
You can check the status and get the results of resize jobs created with this API using the
[Get design resize job API](https://www.canva.dev/docs/connect/api-reference/resizes/get-design-resize-job/).
</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_design_resize_job_request import CreateDesignResizeJobRequest
from openapi_client.models.create_design_resize_job_response import CreateDesignResizeJobResponse
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
    api_instance = openapi_client.ResizeApi(api_client)
    create_design_resize_job_request = {"design_id":"DAGirp_1ZUA","design_type":{"type":"custom","width":1000,"height":1500}} # CreateDesignResizeJobRequest |  (optional)

    try:
        api_response = api_instance.create_design_resize_job(create_design_resize_job_request=create_design_resize_job_request)
        print("The response of ResizeApi->create_design_resize_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ResizeApi->create_design_resize_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_design_resize_job_request** | [**CreateDesignResizeJobRequest**](CreateDesignResizeJobRequest.md)|  | [optional] 

### Return type

[**CreateDesignResizeJobResponse**](CreateDesignResizeJobResponse.md)

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

# **get_design_resize_job**
> GetDesignResizeJobResponse get_design_resize_job(job_id)

<Note>

To use this API, your integration must act on behalf of a user that's on a Canva plan with premium features (such as Canva Pro).

</Note>

Gets the result of a design resize job that was created using the [Create design resize
job API](https://www.canva.dev/docs/connect/api-reference/resizes/create-design-resize-job/).

If the job is successful, the response includes a summary of the new resized design, including its metadata.

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status.
For more information on the workflow for using asynchronous jobs,
see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_resize_job_response import GetDesignResizeJobResponse
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
    api_instance = openapi_client.ResizeApi(api_client)
    job_id = 'job_id_example' # str | The design resize job ID.

    try:
        api_response = api_instance.get_design_resize_job(job_id)
        print("The response of ResizeApi->get_design_resize_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ResizeApi->get_design_resize_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| The design resize job ID. | 

### Return type

[**GetDesignResizeJobResponse**](GetDesignResizeJobResponse.md)

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

