# PresetDesignTypeInput

Provide the common design type.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**name** | [**PresetDesignTypeName**](PresetDesignTypeName.md) |  | 

## Example

```python
from openapi_client.models.preset_design_type_input import PresetDesignTypeInput

# TODO update the JSON string below
json = "{}"
# create an instance of PresetDesignTypeInput from a JSON string
preset_design_type_input_instance = PresetDesignTypeInput.from_json(json)
# print the JSON string representation of the object
print(PresetDesignTypeInput.to_json())

# convert the object into a dict
preset_design_type_input_dict = preset_design_type_input_instance.to_dict()
# create an instance of PresetDesignTypeInput from a dict
preset_design_type_input_from_dict = PresetDesignTypeInput.from_dict(preset_design_type_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


