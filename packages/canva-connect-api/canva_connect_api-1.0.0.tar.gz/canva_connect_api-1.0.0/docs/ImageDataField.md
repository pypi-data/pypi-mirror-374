# ImageDataField

An image for a brand template. You can autofill the brand template with an image by providing its `asset_id`.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 

## Example

```python
from openapi_client.models.image_data_field import ImageDataField

# TODO update the JSON string below
json = "{}"
# create an instance of ImageDataField from a JSON string
image_data_field_instance = ImageDataField.from_json(json)
# print the JSON string representation of the object
print(ImageDataField.to_json())

# convert the object into a dict
image_data_field_dict = image_data_field_instance.to_dict()
# create an instance of ImageDataField from a dict
image_data_field_from_dict = ImageDataField.from_dict(image_data_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


