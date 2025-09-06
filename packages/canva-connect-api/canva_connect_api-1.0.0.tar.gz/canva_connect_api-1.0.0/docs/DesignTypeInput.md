# DesignTypeInput

The desired design type.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**name** | [**PresetDesignTypeName**](PresetDesignTypeName.md) |  | 
**width** | **int** | The width of the design, in pixels. | 
**height** | **int** | The height of the design, in pixels. | 

## Example

```python
from openapi_client.models.design_type_input import DesignTypeInput

# TODO update the JSON string below
json = "{}"
# create an instance of DesignTypeInput from a JSON string
design_type_input_instance = DesignTypeInput.from_json(json)
# print the JSON string representation of the object
print(DesignTypeInput.to_json())

# convert the object into a dict
design_type_input_dict = design_type_input_instance.to_dict()
# create an instance of DesignTypeInput from a dict
design_type_input_from_dict = DesignTypeInput.from_dict(design_type_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


