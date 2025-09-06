# GetDesignResponse

Successful response from a `getDesign` request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**design** | [**Design**](Design.md) |  | 

## Example

```python
from openapi_client.models.get_design_response import GetDesignResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDesignResponse from a JSON string
get_design_response_instance = GetDesignResponse.from_json(json)
# print the JSON string representation of the object
print(GetDesignResponse.to_json())

# convert the object into a dict
get_design_response_dict = get_design_response_instance.to_dict()
# create an instance of GetDesignResponse from a dict
get_design_response_from_dict = GetDesignResponse.from_dict(get_design_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


