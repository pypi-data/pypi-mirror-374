# BrandTemplate

An object representing a brand template with associated metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The brand template ID. | 
**title** | **str** | The brand template title, as shown in the Canva UI. | 
**view_url** | **str** | A URL Canva users can visit to view the brand template. | 
**create_url** | **str** | A URL Canva users can visit to create a new design from the template. | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | [optional] 
**created_at** | **int** | When the brand template was created, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the brand template was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | 

## Example

```python
from openapi_client.models.brand_template import BrandTemplate

# TODO update the JSON string below
json = "{}"
# create an instance of BrandTemplate from a JSON string
brand_template_instance = BrandTemplate.from_json(json)
# print the JSON string representation of the object
print(BrandTemplate.to_json())

# convert the object into a dict
brand_template_dict = brand_template_instance.to_dict()
# create an instance of BrandTemplate from a dict
brand_template_from_dict = BrandTemplate.from_dict(brand_template_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


