# DatasetImageValue

If the data field is an image field.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**asset_id** | **str** | &#x60;asset_id&#x60; of the image to insert into the template element. | 

## Example

```python
from openapi_client.models.dataset_image_value import DatasetImageValue

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetImageValue from a JSON string
dataset_image_value_instance = DatasetImageValue.from_json(json)
# print the JSON string representation of the object
print(DatasetImageValue.to_json())

# convert the object into a dict
dataset_image_value_dict = dataset_image_value_instance.to_dict()
# create an instance of DatasetImageValue from a dict
dataset_image_value_from_dict = DatasetImageValue.from_dict(dataset_image_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


