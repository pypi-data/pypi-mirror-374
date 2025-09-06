# DesignItem

Details about the design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 

## Example

```python
from openapi_client.models.design_item import DesignItem

# TODO update the JSON string below
json = "{}"
# create an instance of DesignItem from a JSON string
design_item_instance = DesignItem.from_json(json)
# print the JSON string representation of the object
print(DesignItem.to_json())

# convert the object into a dict
design_item_dict = design_item_instance.to_dict()
# create an instance of DesignItem from a dict
design_item_from_dict = DesignItem.from_dict(design_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


