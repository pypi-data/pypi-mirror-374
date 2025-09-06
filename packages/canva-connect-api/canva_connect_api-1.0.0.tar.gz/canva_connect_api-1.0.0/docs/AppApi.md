# openapi_client.AppApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_app_jwks**](AppApi.md#get_app_jwks) | **GET** /v1/apps/{appId}/jwks | 


# **get_app_jwks**
> GetAppJwksResponse get_app_jwks(app_id)

Returns the Json Web Key Set (public keys) of an app. These keys are used to
verify JWTs sent to app backends.

### Example


```python
import openapi_client
from openapi_client.models.get_app_jwks_response import GetAppJwksResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AppApi(api_client)
    app_id = 'app_id_example' # str | The app ID.

    try:
        api_response = api_instance.get_app_jwks(app_id)
        print("The response of AppApi->get_app_jwks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppApi->get_app_jwks: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_id** | **str**| The app ID. | 

### Return type

[**GetAppJwksResponse**](GetAppJwksResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

