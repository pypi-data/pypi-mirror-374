# openapi_client.ConnectApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_signing_public_keys**](ConnectApi.md#get_signing_public_keys) | **GET** /v1/connect/keys | 


# **get_signing_public_keys**
> GetSigningPublicKeysResponse get_signing_public_keys()

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

The Keys API (`connect/keys`) is a security measure you can use to verify the authenticity
of webhooks you receive from Canva Connect. The Keys API returns a
[JSON Web Key (JWK)](https://www.rfc-editor.org/rfc/rfc7517#section-2), which you can use to
decrypt the webhook signature and verify it came from Canva and not a potentially malicious
actor. This helps to protect your systems from
[Replay attacks](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/).

The keys returned by the Keys API can rotate. We recommend you cache the keys you receive
from this API where possible, and only access this API when you receive a webhook signed
with an unrecognized key. This allows you to verify webhooks quicker than accessing this API
every time you receive a webhook.

### Example


```python
import openapi_client
from openapi_client.models.get_signing_public_keys_response import GetSigningPublicKeysResponse
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
    api_instance = openapi_client.ConnectApi(api_client)

    try:
        api_response = api_instance.get_signing_public_keys()
        print("The response of ConnectApi->get_signing_public_keys:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectApi->get_signing_public_keys: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetSigningPublicKeysResponse**](GetSigningPublicKeysResponse.md)

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

