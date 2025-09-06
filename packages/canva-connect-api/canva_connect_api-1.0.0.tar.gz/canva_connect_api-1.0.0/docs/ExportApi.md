# openapi_client.ExportApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_design_export_job**](ExportApi.md#create_design_export_job) | **POST** /v1/exports | 
[**get_design_export_job**](ExportApi.md#get_design_export_job) | **GET** /v1/exports/{exportId} | 


# **create_design_export_job**
> CreateDesignExportJobResponse create_design_export_job(create_design_export_job_request=create_design_export_job_request)

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints) to export a file from Canva. Once the exported file is generated, you can download
it using the URL(s) provided. The download URLs are only valid for 24 hours.

The request requires the design ID and the exported file format type.

Supported file formats (and export file type values): PDF (`pdf`), JPG (`jpg`), PNG (`png`), GIF (`gif`), Microsoft PowerPoint (`pptx`), and MP4 (`mp4`).

<Note>

For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints). You can check the status and get the results of export jobs created with this API using the [Get design export job API](https://www.canva.dev/docs/connect/api-reference/exports/get-design-export-job/).

</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_design_export_job_request import CreateDesignExportJobRequest
from openapi_client.models.create_design_export_job_response import CreateDesignExportJobResponse
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
    api_instance = openapi_client.ExportApi(api_client)
    create_design_export_job_request = openapi_client.CreateDesignExportJobRequest() # CreateDesignExportJobRequest |  (optional)

    try:
        api_response = api_instance.create_design_export_job(create_design_export_job_request=create_design_export_job_request)
        print("The response of ExportApi->create_design_export_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->create_design_export_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_design_export_job_request** | [**CreateDesignExportJobRequest**](CreateDesignExportJobRequest.md)|  | [optional] 

### Return type

[**CreateDesignExportJobResponse**](CreateDesignExportJobResponse.md)

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

# **get_design_export_job**
> GetDesignExportJobResponse get_design_export_job(export_id)

Gets the result of a design export job that was created using the [Create design export job API](https://www.canva.dev/docs/connect/api-reference/exports/create-design-export-job/).

If the job is successful, the response includes an array
of download URLs. Depending on the design type and export format, there is a download URL for each page in the design. The download URLs are only valid for 24 hours.

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status. For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_export_job_response import GetDesignExportJobResponse
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
    api_instance = openapi_client.ExportApi(api_client)
    export_id = 'export_id_example' # str | The export job ID.

    try:
        api_response = api_instance.get_design_export_job(export_id)
        print("The response of ExportApi->get_design_export_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->get_design_export_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **export_id** | **str**| The export job ID. | 

### Return type

[**GetDesignExportJobResponse**](GetDesignExportJobResponse.md)

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

