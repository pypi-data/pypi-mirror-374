# openapi_client.UserApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_user_capabilities**](UserApi.md#get_user_capabilities) | **GET** /v1/users/me/capabilities | 
[**get_user_profile**](UserApi.md#get_user_profile) | **GET** /v1/users/me/profile | 
[**users_me**](UserApi.md#users_me) | **GET** /v1/users/me | 


# **get_user_capabilities**
> GetUserCapabilitiesResponse get_user_capabilities()

Lists the API capabilities for the user account associated with the provided access token. For more information, see [Capabilities](https://www.canva.dev/docs/connect/capabilities/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_user_capabilities_response import GetUserCapabilitiesResponse
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
    api_instance = openapi_client.UserApi(api_client)

    try:
        api_response = api_instance.get_user_capabilities()
        print("The response of UserApi->get_user_capabilities:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->get_user_capabilities: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetUserCapabilitiesResponse**](GetUserCapabilitiesResponse.md)

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

# **get_user_profile**
> UserProfileResponse get_user_profile()

Currently, this returns the display name of the user account associated with the provided access token. More user information is expected to be included in the future.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.user_profile_response import UserProfileResponse
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
    api_instance = openapi_client.UserApi(api_client)

    try:
        api_response = api_instance.get_user_profile()
        print("The response of UserApi->get_user_profile:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->get_user_profile: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**UserProfileResponse**](UserProfileResponse.md)

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

# **users_me**
> UsersMeResponse users_me()

Returns the User ID and Team ID of the user
account associated with the provided access token.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.users_me_response import UsersMeResponse
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
    api_instance = openapi_client.UserApi(api_client)

    try:
        api_response = api_instance.users_me()
        print("The response of UserApi->users_me:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->users_me: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**UsersMeResponse**](UsersMeResponse.md)

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

