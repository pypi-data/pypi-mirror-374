# openapi_client.DesignImportApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_design_import_job**](DesignImportApi.md#create_design_import_job) | **POST** /v1/imports | 
[**create_url_import_job**](DesignImportApi.md#create_url_import_job) | **POST** /v1/url-imports | 
[**get_design_import_job**](DesignImportApi.md#get_design_import_job) | **GET** /v1/imports/{jobId} | 
[**get_url_import_job**](DesignImportApi.md#get_url_import_job) | **GET** /v1/url-imports/{jobId} | 


# **create_design_import_job**
> CreateDesignImportJobResponse create_design_import_job(import_metadata, body)

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints) to import an external file as a new design in Canva.

The request format for this endpoint has an `application/octet-stream` body of bytes,
and the information about the import is provided using an `Import-Metadata` header.

Supported file types for imports are listed in [Design imports overview](https://www.canva.dev/docs/connect/api-reference/design-imports/#supported-file-types).

<Note>

For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints). You can check the status and get the results of design import jobs created with this API using the [Get design import job API](https://www.canva.dev/docs/connect/api-reference/design-imports/get-design-import-job/).

</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_design_import_job_response import CreateDesignImportJobResponse
from openapi_client.models.design_import_metadata import DesignImportMetadata
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
    api_instance = openapi_client.DesignImportApi(api_client)
    import_metadata = openapi_client.DesignImportMetadata() # DesignImportMetadata | 
    body = None # bytearray | Binary of the file to import.

    try:
        api_response = api_instance.create_design_import_job(import_metadata, body)
        print("The response of DesignImportApi->create_design_import_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignImportApi->create_design_import_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **import_metadata** | [**DesignImportMetadata**](.md)|  | 
 **body** | **bytearray**| Binary of the file to import. | 

### Return type

[**CreateDesignImportJobResponse**](CreateDesignImportJobResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_url_import_job**
> CreateUrlImportJobResponse create_url_import_job(create_url_import_job_request)

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints) to import an external file from a URL as a new design in Canva.

Supported file types for imports are listed in [Design imports overview](https://www.canva.dev/docs/connect/api-reference/design-imports/#supported-file-types).

<Note>

For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints). You can check the status and get the results of design import jobs created with this API using the [Get URL import job API](https://www.canva.dev/docs/connect/api-reference/design-imports/get-url-import-job/).

</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_url_import_job_request import CreateUrlImportJobRequest
from openapi_client.models.create_url_import_job_response import CreateUrlImportJobResponse
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
    api_instance = openapi_client.DesignImportApi(api_client)
    create_url_import_job_request = openapi_client.CreateUrlImportJobRequest() # CreateUrlImportJobRequest | 

    try:
        api_response = api_instance.create_url_import_job(create_url_import_job_request)
        print("The response of DesignImportApi->create_url_import_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignImportApi->create_url_import_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_url_import_job_request** | [**CreateUrlImportJobRequest**](CreateUrlImportJobRequest.md)|  | 

### Return type

[**CreateUrlImportJobResponse**](CreateUrlImportJobResponse.md)

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

# **get_design_import_job**
> GetDesignImportJobResponse get_design_import_job(job_id)

Gets the result of a design import job created using the [Create design import job API](https://www.canva.dev/docs/connect/api-reference/design-imports/create-design-import-job/).

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status. For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_import_job_response import GetDesignImportJobResponse
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
    api_instance = openapi_client.DesignImportApi(api_client)
    job_id = 'f81b26fd-a33d-4c2d-9e8c-4a7aca798b17' # str | The design import job ID.

    try:
        api_response = api_instance.get_design_import_job(job_id)
        print("The response of DesignImportApi->get_design_import_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignImportApi->get_design_import_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| The design import job ID. | 

### Return type

[**GetDesignImportJobResponse**](GetDesignImportJobResponse.md)

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

# **get_url_import_job**
> GetUrlImportJobResponse get_url_import_job(job_id)

Gets the result of a URL import job created using the [Create URL import job API](https://www.canva.dev/docs/connect/api-reference/design-imports/create-url-import-job/).

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status. For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_url_import_job_response import GetUrlImportJobResponse
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
    api_instance = openapi_client.DesignImportApi(api_client)
    job_id = 'f81b26fd-a33d-4c2d-9e8c-4a7aca798b17' # str | The ID of the URL import job.

    try:
        api_response = api_instance.get_url_import_job(job_id)
        print("The response of DesignImportApi->get_url_import_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignImportApi->get_url_import_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| The ID of the URL import job. | 

### Return type

[**GetUrlImportJobResponse**](GetUrlImportJobResponse.md)

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

