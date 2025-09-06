# GetSigningPublicKeysResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**keys** | [**List[EdDsaJwk]**](EdDsaJwk.md) | A Json Web Key Set (JWKS) with public keys used for signing webhooks. You can use this JWKS to verify that a webhook was sent from Canva. | 

## Example

```python
from openapi_client.models.get_signing_public_keys_response import GetSigningPublicKeysResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSigningPublicKeysResponse from a JSON string
get_signing_public_keys_response_instance = GetSigningPublicKeysResponse.from_json(json)
# print the JSON string representation of the object
print(GetSigningPublicKeysResponse.to_json())

# convert the object into a dict
get_signing_public_keys_response_dict = get_signing_public_keys_response_instance.to_dict()
# create an instance of GetSigningPublicKeysResponse from a dict
get_signing_public_keys_response_from_dict = GetSigningPublicKeysResponse.from_dict(get_signing_public_keys_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


