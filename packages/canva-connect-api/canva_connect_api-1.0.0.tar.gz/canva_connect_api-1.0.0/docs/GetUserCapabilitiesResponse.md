# GetUserCapabilitiesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**capabilities** | [**List[Capability]**](Capability.md) |  | [optional] 

## Example

```python
from openapi_client.models.get_user_capabilities_response import GetUserCapabilitiesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetUserCapabilitiesResponse from a JSON string
get_user_capabilities_response_instance = GetUserCapabilitiesResponse.from_json(json)
# print the JSON string representation of the object
print(GetUserCapabilitiesResponse.to_json())

# convert the object into a dict
get_user_capabilities_response_dict = get_user_capabilities_response_instance.to_dict()
# create an instance of GetUserCapabilitiesResponse from a dict
get_user_capabilities_response_from_dict = GetUserCapabilitiesResponse.from_dict(get_user_capabilities_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


