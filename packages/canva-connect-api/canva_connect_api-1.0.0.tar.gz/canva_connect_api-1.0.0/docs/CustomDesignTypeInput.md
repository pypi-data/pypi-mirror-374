# CustomDesignTypeInput

Provide the width and height to define a custom design type.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**width** | **int** | The width of the design, in pixels. | 
**height** | **int** | The height of the design, in pixels. | 

## Example

```python
from openapi_client.models.custom_design_type_input import CustomDesignTypeInput

# TODO update the JSON string below
json = "{}"
# create an instance of CustomDesignTypeInput from a JSON string
custom_design_type_input_instance = CustomDesignTypeInput.from_json(json)
# print the JSON string representation of the object
print(CustomDesignTypeInput.to_json())

# convert the object into a dict
custom_design_type_input_dict = custom_design_type_input_instance.to_dict()
# create an instance of CustomDesignTypeInput from a dict
custom_design_type_input_from_dict = CustomDesignTypeInput.from_dict(custom_design_type_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


