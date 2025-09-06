# openapi_client.AssetApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_asset_upload_job**](AssetApi.md#create_asset_upload_job) | **POST** /v1/asset-uploads | 
[**create_url_asset_upload_job**](AssetApi.md#create_url_asset_upload_job) | **POST** /v1/url-asset-uploads | 
[**delete_asset**](AssetApi.md#delete_asset) | **DELETE** /v1/assets/{assetId} | 
[**get_asset**](AssetApi.md#get_asset) | **GET** /v1/assets/{assetId} | 
[**get_asset_upload_job**](AssetApi.md#get_asset_upload_job) | **GET** /v1/asset-uploads/{jobId} | 
[**get_url_asset_upload_job**](AssetApi.md#get_url_asset_upload_job) | **GET** /v1/url-asset-uploads/{jobId} | 
[**update_asset**](AssetApi.md#update_asset) | **PATCH** /v1/assets/{assetId} | 


# **create_asset_upload_job**
> CreateAssetUploadJobResponse create_asset_upload_job(asset_upload_metadata, body)

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints) to upload an asset to the user's content library. Supported file types for assets are listed in the [Assets API overview](https://www.canva.dev/docs/connect/api-reference/assets/).

The request format for this endpoint is an `application/octet-stream` body of bytes. Attach
information about the upload using an `Asset-Upload-Metadata` header.


<Note>

For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints). You can check the status and get the results of asset upload jobs created with this API using the [Get asset upload job API](https://www.canva.dev/docs/connect/api-reference/assets/get-asset-upload-job/).

</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.asset_upload_metadata import AssetUploadMetadata
from openapi_client.models.create_asset_upload_job_response import CreateAssetUploadJobResponse
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
    api_instance = openapi_client.AssetApi(api_client)
    asset_upload_metadata = openapi_client.AssetUploadMetadata() # AssetUploadMetadata | 
    body = None # bytearray | Binary of the asset to upload.

    try:
        api_response = api_instance.create_asset_upload_job(asset_upload_metadata, body)
        print("The response of AssetApi->create_asset_upload_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->create_asset_upload_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_upload_metadata** | [**AssetUploadMetadata**](.md)|  | 
 **body** | **bytearray**| Binary of the asset to upload. | 

### Return type

[**CreateAssetUploadJobResponse**](CreateAssetUploadJobResponse.md)

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

# **create_url_asset_upload_job**
> CreateUrlAssetUploadJobResponse create_url_asset_upload_job(create_url_asset_upload_job_request)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Starts a new [asynchronous job](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints) to upload an asset from a URL to the user's content library. Supported file types for assets are listed in the [Assets API overview](https://www.canva.dev/docs/connect/api-reference/assets/).

<Note>
 Uploading a video asset from a URL is limited to a maximum 100MB file size. For importing larger video files, use the [Create asset upload job API](https://www.canva.dev/docs/connect/api-reference/assets/create-asset-upload-job/).
</Note>

<Note>
For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints). You can check the status and get the results of asset upload jobs created with this API using the [Get asset upload job via URL API](https://www.canva.dev/docs/connect/api-reference/assets/get-url-asset-upload-job/).
</Note>

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_url_asset_upload_job_request import CreateUrlAssetUploadJobRequest
from openapi_client.models.create_url_asset_upload_job_response import CreateUrlAssetUploadJobResponse
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
    api_instance = openapi_client.AssetApi(api_client)
    create_url_asset_upload_job_request = openapi_client.CreateUrlAssetUploadJobRequest() # CreateUrlAssetUploadJobRequest | 

    try:
        api_response = api_instance.create_url_asset_upload_job(create_url_asset_upload_job_request)
        print("The response of AssetApi->create_url_asset_upload_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->create_url_asset_upload_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_url_asset_upload_job_request** | [**CreateUrlAssetUploadJobRequest**](CreateUrlAssetUploadJobRequest.md)|  | 

### Return type

[**CreateUrlAssetUploadJobResponse**](CreateUrlAssetUploadJobResponse.md)

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

# **delete_asset**
> delete_asset(asset_id)

You can delete an asset by specifying its `assetId`. This operation mirrors the behavior
in the Canva UI. Deleting an item moves it to the trash.
Deleting an asset doesn't remove it from designs that already use it.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
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
    api_instance = openapi_client.AssetApi(api_client)
    asset_id = 'asset_id_example' # str | The ID of the asset.

    try:
        api_instance.delete_asset(asset_id)
    except Exception as e:
        print("Exception when calling AssetApi->delete_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_id** | **str**| The ID of the asset. | 

### Return type

void (empty response body)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_asset**
> GetAssetResponse get_asset(asset_id)

You can retrieve the metadata of an asset by specifying its `assetId`.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_asset_response import GetAssetResponse
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
    api_instance = openapi_client.AssetApi(api_client)
    asset_id = 'asset_id_example' # str | The ID of the asset.

    try:
        api_response = api_instance.get_asset(asset_id)
        print("The response of AssetApi->get_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->get_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_id** | **str**| The ID of the asset. | 

### Return type

[**GetAssetResponse**](GetAssetResponse.md)

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

# **get_asset_upload_job**
> GetAssetUploadJobResponse get_asset_upload_job(job_id)

Get the result of an asset upload job that was created using the [Create asset upload job API](https://www.canva.dev/docs/connect/api-reference/assets/create-asset-upload-job/).

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status. For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_asset_upload_job_response import GetAssetUploadJobResponse
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
    api_instance = openapi_client.AssetApi(api_client)
    job_id = 'job_id_example' # str | The asset upload job ID.

    try:
        api_response = api_instance.get_asset_upload_job(job_id)
        print("The response of AssetApi->get_asset_upload_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->get_asset_upload_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| The asset upload job ID. | 

### Return type

[**GetAssetUploadJobResponse**](GetAssetUploadJobResponse.md)

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

# **get_url_asset_upload_job**
> GetUrlAssetUploadJobResponse get_url_asset_upload_job(job_id)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Get the result of an asset upload job that was created using the [Create asset upload job via URL API](https://www.canva.dev/docs/connect/api-reference/assets/create-url-asset-upload-job/).

You might need to make multiple requests to this endpoint until you get a `success` or `failed` status. For more information on the workflow for using asynchronous jobs, see [API requests and responses](https://www.canva.dev/docs/connect/api-requests-responses/#asynchronous-job-endpoints).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_url_asset_upload_job_response import GetUrlAssetUploadJobResponse
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
    api_instance = openapi_client.AssetApi(api_client)
    job_id = 'job_id_example' # str | The asset upload job ID.

    try:
        api_response = api_instance.get_url_asset_upload_job(job_id)
        print("The response of AssetApi->get_url_asset_upload_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->get_url_asset_upload_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| The asset upload job ID. | 

### Return type

[**GetUrlAssetUploadJobResponse**](GetUrlAssetUploadJobResponse.md)

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

# **update_asset**
> UpdateAssetResponse update_asset(asset_id, update_asset_request=update_asset_request)

You can update the name and tags of an asset by specifying its `assetId`. Updating the tags
replaces all existing tags of the asset.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.update_asset_request import UpdateAssetRequest
from openapi_client.models.update_asset_response import UpdateAssetResponse
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
    api_instance = openapi_client.AssetApi(api_client)
    asset_id = 'asset_id_example' # str | The ID of the asset.
    update_asset_request = openapi_client.UpdateAssetRequest() # UpdateAssetRequest |  (optional)

    try:
        api_response = api_instance.update_asset(asset_id, update_asset_request=update_asset_request)
        print("The response of AssetApi->update_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->update_asset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_id** | **str**| The ID of the asset. | 
 **update_asset_request** | [**UpdateAssetRequest**](UpdateAssetRequest.md)|  | [optional] 

### Return type

[**UpdateAssetResponse**](UpdateAssetResponse.md)

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

