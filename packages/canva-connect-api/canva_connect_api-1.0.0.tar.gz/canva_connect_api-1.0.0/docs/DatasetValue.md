# DatasetValue

The data field to autofill.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**asset_id** | **str** | &#x60;asset_id&#x60; of the image to insert into the template element. | 
**text** | **str** | Text to insert into the template element. | 
**chart_data** | [**DataTable**](DataTable.md) |  | 

## Example

```python
from openapi_client.models.dataset_value import DatasetValue

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetValue from a JSON string
dataset_value_instance = DatasetValue.from_json(json)
# print the JSON string representation of the object
print(DatasetValue.to_json())

# convert the object into a dict
dataset_value_dict = dataset_value_instance.to_dict()
# create an instance of DatasetValue from a dict
dataset_value_from_dict = DatasetValue.from_dict(dataset_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


