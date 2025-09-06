# IntrospectTokenResponse

Introspection result of access or refresh tokens

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | Whether the access token is active.  If &#x60;true&#x60;, the access token is valid and active. If &#x60;false&#x60;, the access token is invalid.  | 
**scope** | **str** | The [scopes](https://www.canva.dev/docs/connect/appendix/scopes/) that the token has been granted. | [optional] 
**client** | **str** | The ID of the client that requested the token. | [optional] 
**exp** | **int** | The expiration time of the token, as a [Unix timestamp](https://en.wikipedia.org/wiki/Unix_time) in seconds. | [optional] 
**iat** | **int** | When the token was issued, as a [Unix timestamp](https://en.wikipedia.org/wiki/Unix_time) in seconds. | [optional] 
**nbf** | **int** | The \&quot;not before\&quot; time of the token, which specifies the time before which the access token most not be accepted, as a [Unix timestamp](https://en.wikipedia.org/wiki/Unix_time) in seconds. | [optional] 
**jti** | **str** | A unique ID for the access token. | [optional] 
**sub** | **str** | The subject of the claim. This is the ID of the Canva user that the access token acts on behalf of.  This is an obfuscated value, so a single user has a unique ID for each integration. If the same user authorizes another integration, their ID in that other integration is different.  | [optional] 

## Example

```python
from openapi_client.models.introspect_token_response import IntrospectTokenResponse

# TODO update the JSON string below
json = "{}"
# create an instance of IntrospectTokenResponse from a JSON string
introspect_token_response_instance = IntrospectTokenResponse.from_json(json)
# print the JSON string representation of the object
print(IntrospectTokenResponse.to_json())

# convert the object into a dict
introspect_token_response_dict = introspect_token_response_instance.to_dict()
# create an instance of IntrospectTokenResponse from a dict
introspect_token_response_from_dict = IntrospectTokenResponse.from_dict(introspect_token_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


