# CreateDesignResponse

Details about the new design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**design** | [**Design**](Design.md) |  | 

## Example

```python
from openapi_client.models.create_design_response import CreateDesignResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignResponse from a JSON string
create_design_response_instance = CreateDesignResponse.from_json(json)
# print the JSON string representation of the object
print(CreateDesignResponse.to_json())

# convert the object into a dict
create_design_response_dict = create_design_response_instance.to_dict()
# create an instance of CreateDesignResponse from a dict
create_design_response_from_dict = CreateDesignResponse.from_dict(create_design_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


