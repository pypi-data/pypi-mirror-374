# GetAppJwksResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**keys** | [**List[JsonWebKey]**](JsonWebKey.md) | The value of the \&quot;keys\&quot; parameter is an array of JWK values. The order of keys has no meaning. | 

## Example

```python
from openapi_client.models.get_app_jwks_response import GetAppJwksResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAppJwksResponse from a JSON string
get_app_jwks_response_instance = GetAppJwksResponse.from_json(json)
# print the JSON string representation of the object
print(GetAppJwksResponse.to_json())

# convert the object into a dict
get_app_jwks_response_dict = get_app_jwks_response_instance.to_dict()
# create an instance of GetAppJwksResponse from a dict
get_app_jwks_response_from_dict = GetAppJwksResponse.from_dict(get_app_jwks_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


