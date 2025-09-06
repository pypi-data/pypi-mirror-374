# openapi_client.OauthApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**exchange_access_token**](OauthApi.md#exchange_access_token) | **POST** /v1/oauth/token | 
[**introspect_token**](OauthApi.md#introspect_token) | **POST** /v1/oauth/introspect | 
[**revoke_tokens**](OauthApi.md#revoke_tokens) | **POST** /v1/oauth/revoke | 


# **exchange_access_token**
> ExchangeAccessTokenResponse exchange_access_token(grant_type=grant_type, code_verifier=code_verifier, code=code, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, refresh_token=refresh_token, scope=scope)

This endpoint implements the OAuth 2.0 `token` endpoint, as part of the Authorization Code flow with Proof Key for Code Exchange (PKCE). For more information, see [Authentication](https://www.canva.dev/docs/connect/authentication/).

To generate an access token, you must provide one of the following:

- An authorization code
- A refresh token

Generating a token using either an authorization code or a refresh token allows your integration to act on behalf of a user. You must first [obtain user authorization and get an authorization code](https://www.canva.dev/docs/connect/authentication/#obtain-user-authorization).

Access tokens may be up to 4 KB in size, and are only valid for a specified period of time. The expiry time (currently 4 hours) is shown in the endpoint response and is subject to change.

**Endpoint authentication**

Requests to this endpoint require authentication with your client ID and client secret, using _one_ of the following methods:

- **Basic access authentication** (Recommended): For [basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication), the `{credentials}` string must be a Base64 encoded value of `{client id}:{client secret}`.
- **Body parameters**: Provide your integration's credentials using the `client_id` and `client_secret` body parameters.

This endpoint can't be called from a user's web-browser client because it uses client authentication with client secrets. Requests must come from your integration's backend, otherwise they'll be blocked by Canva's [Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) policy.

**Generate an access token using an authorization code**

To generate an access token with an authorization code, you must:

- Set `grant_type` to `authorization_code`.
- Provide the `code_verifier` value that you generated when creating the user authorization URL.
- Provide the authorization code you received after the user authorized the integration.

**Generate an access token using a refresh token**

Using the `refresh_token` value from a previous user token request, you can get a new access token with the same or smaller scope as the previous one, but with a refreshed expiry time. You will also receive a new refresh token that you can use to refresh the access token again.

To refresh an existing access token, you must:

- Set `grant_type` to `refresh_token`.
- Provide the `refresh_token` from a previous token request.

### Example

* Basic Authentication (basicAuth):

```python
import openapi_client
from openapi_client.models.exchange_access_token_response import ExchangeAccessTokenResponse
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

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.OauthApi(api_client)
    grant_type = 'grant_type_example' # str | For generating an access token using a refresh token. (optional)
    code_verifier = 'code_verifier_example' # str | The `code_verifier` value that you generated when creating the user authorization URL. (optional)
    code = 'code_example' # str | The authorization code you received after the user authorized the integration. (optional)
    client_id = 'client_id_example' # str | Your integration's unique ID, for authenticating the request.  NOTE: We recommend that you use basic access authentication instead of specifying `client_id` and `client_secret` as body parameters.  (optional)
    client_secret = 'client_secret_example' # str | Your integration's client secret, for authenticating the request. Begins with `cnvca`.  NOTE: We recommend that you use basic access authentication instead of specifying `client_id` and `client_secret` as body parameters.  (optional)
    redirect_uri = 'redirect_uri_example' # str | Only required if a redirect URL was supplied when you [created the user authorization URL](https://www.canva.dev/docs/connect/authentication/#create-the-authorization-url).  Must be one of those already specified by the client. If not supplied, the first redirect_uri defined for the client will be used by default.  (optional)
    refresh_token = 'refresh_token_example' # str | The refresh token to be exchanged. You can copy this value from the successful response received when generating an access token. (optional)
    scope = 'scope_example' # str | Optional scope value when refreshing an access token. Separate multiple [scopes](https://www.canva.dev/docs/connect/appendix/scopes/) with a single space between each scope.  The requested scope cannot include any permissions not already granted, so this parameter allows you to limit the scope when refreshing a token. If omitted, the scope for the token remains unchanged.  (optional)

    try:
        api_response = api_instance.exchange_access_token(grant_type=grant_type, code_verifier=code_verifier, code=code, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, refresh_token=refresh_token, scope=scope)
        print("The response of OauthApi->exchange_access_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OauthApi->exchange_access_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **grant_type** | **str**| For generating an access token using a refresh token. | [optional] 
 **code_verifier** | **str**| The &#x60;code_verifier&#x60; value that you generated when creating the user authorization URL. | [optional] 
 **code** | **str**| The authorization code you received after the user authorized the integration. | [optional] 
 **client_id** | **str**| Your integration&#39;s unique ID, for authenticating the request.  NOTE: We recommend that you use basic access authentication instead of specifying &#x60;client_id&#x60; and &#x60;client_secret&#x60; as body parameters.  | [optional] 
 **client_secret** | **str**| Your integration&#39;s client secret, for authenticating the request. Begins with &#x60;cnvca&#x60;.  NOTE: We recommend that you use basic access authentication instead of specifying &#x60;client_id&#x60; and &#x60;client_secret&#x60; as body parameters.  | [optional] 
 **redirect_uri** | **str**| Only required if a redirect URL was supplied when you [created the user authorization URL](https://www.canva.dev/docs/connect/authentication/#create-the-authorization-url).  Must be one of those already specified by the client. If not supplied, the first redirect_uri defined for the client will be used by default.  | [optional] 
 **refresh_token** | **str**| The refresh token to be exchanged. You can copy this value from the successful response received when generating an access token. | [optional] 
 **scope** | **str**| Optional scope value when refreshing an access token. Separate multiple [scopes](https://www.canva.dev/docs/connect/appendix/scopes/) with a single space between each scope.  The requested scope cannot include any permissions not already granted, so this parameter allows you to limit the scope when refreshing a token. If omitted, the scope for the token remains unchanged.  | [optional] 

### Return type

[**ExchangeAccessTokenResponse**](ExchangeAccessTokenResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **introspect_token**
> IntrospectTokenResponse introspect_token(token, client_id=client_id, client_secret=client_secret)

Introspect an access token to see whether it is valid and active. You can also verify some token properties, such as its claims, scopes, and validity times.

Requests to this endpoint require authentication with your client ID and client secret, using _one_ of the following methods:

- **Basic access authentication** (Recommended): For [basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication), the `{credentials}` string must be a Base64 encoded value of `{client id}:{client secret}`.
- **Body parameters**: Provide your integration's credentials using the `client_id` and `client_secret` body parameters.

This endpoint can't be called from a user's web-browser client because it uses client authentication with client secrets. Requests must come from your integration's backend, otherwise they'll be blocked by Canva's [Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) policy.

### Example

* Basic Authentication (basicAuth):

```python
import openapi_client
from openapi_client.models.introspect_token_response import IntrospectTokenResponse
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

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.OauthApi(api_client)
    token = 'token_example' # str | The token to introspect.
    client_id = 'client_id_example' # str | Your integration's unique ID, for authenticating the request.  NOTE: We recommend that you use basic access authentication instead of specifying `client_id` and `client_secret` as body parameters.  (optional)
    client_secret = 'client_secret_example' # str | Your integration's client secret, for authenticating the request. Begins with `cnvca`.  NOTE: We recommend that you use basic access authentication instead of specifying `client_id` and `client_secret` as body parameters.  (optional)

    try:
        api_response = api_instance.introspect_token(token, client_id=client_id, client_secret=client_secret)
        print("The response of OauthApi->introspect_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OauthApi->introspect_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| The token to introspect. | 
 **client_id** | **str**| Your integration&#39;s unique ID, for authenticating the request.  NOTE: We recommend that you use basic access authentication instead of specifying &#x60;client_id&#x60; and &#x60;client_secret&#x60; as body parameters.  | [optional] 
 **client_secret** | **str**| Your integration&#39;s client secret, for authenticating the request. Begins with &#x60;cnvca&#x60;.  NOTE: We recommend that you use basic access authentication instead of specifying &#x60;client_id&#x60; and &#x60;client_secret&#x60; as body parameters.  | [optional] 

### Return type

[**IntrospectTokenResponse**](IntrospectTokenResponse.md)

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_tokens**
> object revoke_tokens(token, client_id=client_id, client_secret=client_secret)

Revoke an access token or a refresh token.

If you revoke a _refresh token_, be aware that:

- The refresh token's lineage is also revoked. This means that access tokens created from that refresh token are also revoked.
- The user's consent for your integration is also revoked. This means that the user must go through the OAuth process again to use your integration.

Requests to this endpoint require authentication with your client ID and client secret, using _one_ of the following methods:

- **Basic access authentication** (Recommended): For [basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication), the `{credentials}` string must be a Base64 encoded value of `{client id}:{client secret}`.
- **Body parameters**: Provide your integration's credentials using the `client_id` and `client_secret` body parameters.

This endpoint can't be called from a user's web-browser client because it uses client authentication with client secrets. Requests must come from your integration's backend, otherwise they'll be blocked by Canva's [Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) policy.

### Example

* Basic Authentication (basicAuth):

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

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.OauthApi(api_client)
    token = 'token_example' # str | The token to revoke.
    client_id = 'client_id_example' # str | Your integration's unique ID, for authenticating the request.  NOTE: We recommend that you use basic access authentication instead of specifying `client_id` and `client_secret` as body parameters.  (optional)
    client_secret = 'client_secret_example' # str | Your integration's client secret, for authenticating the request. Begins with `cnvca`.  NOTE: We recommend that you use basic access authentication instead of specifying `client_id` and `client_secret` as body parameters.  (optional)

    try:
        api_response = api_instance.revoke_tokens(token, client_id=client_id, client_secret=client_secret)
        print("The response of OauthApi->revoke_tokens:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OauthApi->revoke_tokens: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| The token to revoke. | 
 **client_id** | **str**| Your integration&#39;s unique ID, for authenticating the request.  NOTE: We recommend that you use basic access authentication instead of specifying &#x60;client_id&#x60; and &#x60;client_secret&#x60; as body parameters.  | [optional] 
 **client_secret** | **str**| Your integration&#39;s client secret, for authenticating the request. Begins with &#x60;cnvca&#x60;.  NOTE: We recommend that you use basic access authentication instead of specifying &#x60;client_id&#x60; and &#x60;client_secret&#x60; as body parameters.  | [optional] 

### Return type

**object**

### Authorization

[basicAuth](../README.md#basicAuth)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

