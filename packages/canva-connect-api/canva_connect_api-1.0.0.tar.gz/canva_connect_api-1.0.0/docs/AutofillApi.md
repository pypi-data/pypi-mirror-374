# openapi_client.AutofillApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_design_autofill_job**](AutofillApi.md#create_design_autofill_job) | **POST** /v1/autofills | 
[**get_design_autofill_job**](AutofillApi.md#get_design_autofill_job) | **GET** /v1/autofills/{jobId} | 


# **create_design_autofill_job**
> CreateDesignAutofillJobResponse create_design_autofill_job(create_design_autofill_job_request=create_design_autofill_job_request)

<Warning>

Soon, all brand template IDs will be updated to a new format. If your integration stores brand template IDs, you'll need to migrate to use the new IDs. After we implement this change, you'll have 6 months to migrate before the old IDs are removed.

</Warning>

<Note>

To use this API, your integration must act on behalf of a user that's a member of a [Canva Enterprise](https://www.canva.com/enterprise/) organization.

</Note>

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints) to autofill a Canva design using a brand template and input data.

To get a list of input data fields, use the [Get brand template dataset
API](https://www.canva.dev/docs/connect/api-reference/brand-templates/get-brand-template-dataset/).

Available data field types to autofill include:

- Images
- Text
- Charts

  WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version.

<Note>

For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints). You can check the status and get the results of autofill jobs created with this API using the [Get design autofill job API](https://www.canva.dev/docs/connect/api-reference/autofills/get-design-autofill-job/).

</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_design_autofill_job_request import CreateDesignAutofillJobRequest
from openapi_client.models.create_design_autofill_job_response import CreateDesignAutofillJobResponse
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
    api_instance = openapi_client.AutofillApi(api_client)
    create_design_autofill_job_request = openapi_client.CreateDesignAutofillJobRequest() # CreateDesignAutofillJobRequest |  (optional)

    try:
        api_response = api_instance.create_design_autofill_job(create_design_autofill_job_request=create_design_autofill_job_request)
        print("The response of AutofillApi->create_design_autofill_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AutofillApi->create_design_autofill_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_design_autofill_job_request** | [**CreateDesignAutofillJobRequest**](CreateDesignAutofillJobRequest.md)|  | [optional] 

### Return type

[**CreateDesignAutofillJobResponse**](CreateDesignAutofillJobResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_design_autofill_job**
> GetDesignAutofillJobResponse get_design_autofill_job(job_id)

<Note>

To use this API, your integration must act on behalf of a user that's a member of a [Canva Enterprise](https://www.canva.com/enterprise/) organization.

</Note>

Get the result of a design autofill job that was created using the [Create design autofill job
API](https://www.canva.dev/docs/connect/api-reference/autofills/create-design-autofill-job/).

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status. For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_autofill_job_response import GetDesignAutofillJobResponse
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
    api_instance = openapi_client.AutofillApi(api_client)
    job_id = 'job_id_example' # str | The design autofill job ID.

    try:
        api_response = api_instance.get_design_autofill_job(job_id)
        print("The response of AutofillApi->get_design_autofill_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AutofillApi->get_design_autofill_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| The design autofill job ID. | 

### Return type

[**GetDesignAutofillJobResponse**](GetDesignAutofillJobResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**404** | Not Found |  -  |
**403** | Forbidden |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

