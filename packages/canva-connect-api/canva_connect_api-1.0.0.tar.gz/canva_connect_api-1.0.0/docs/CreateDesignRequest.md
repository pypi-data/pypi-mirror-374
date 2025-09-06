# CreateDesignRequest

Body parameters for creating a new design. At least one of `design_type` or `asset_id` must be defined to create a new design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**design_type** | [**DesignTypeInput**](DesignTypeInput.md) |  | [optional] 
**asset_id** | **str** | The ID of an asset to insert into the created design. Currently, this only supports image assets. | [optional] 
**title** | **str** | The name of the design. | [optional] 

## Example

```python
from openapi_client.models.create_design_request import CreateDesignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignRequest from a JSON string
create_design_request_instance = CreateDesignRequest.from_json(json)
# print the JSON string representation of the object
print(CreateDesignRequest.to_json())

# convert the object into a dict
create_design_request_dict = create_design_request_instance.to_dict()
# create an instance of CreateDesignRequest from a dict
create_design_request_from_dict = CreateDesignRequest.from_dict(create_design_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


