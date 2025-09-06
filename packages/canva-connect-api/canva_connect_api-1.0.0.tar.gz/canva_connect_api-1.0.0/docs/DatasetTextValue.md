# DatasetTextValue

If the data field is a text field.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**text** | **str** | Text to insert into the template element. | 

## Example

```python
from openapi_client.models.dataset_text_value import DatasetTextValue

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetTextValue from a JSON string
dataset_text_value_instance = DatasetTextValue.from_json(json)
# print the JSON string representation of the object
print(DatasetTextValue.to_json())

# convert the object into a dict
dataset_text_value_dict = dataset_text_value_instance.to_dict()
# create an instance of DatasetTextValue from a dict
dataset_text_value_from_dict = DatasetTextValue.from_dict(dataset_text_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


