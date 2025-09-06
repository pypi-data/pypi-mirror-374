# GetBrandTemplateResponse

Successful response from a `getBrandTemplate` request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**brand_template** | [**BrandTemplate**](BrandTemplate.md) |  | 

## Example

```python
from openapi_client.models.get_brand_template_response import GetBrandTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBrandTemplateResponse from a JSON string
get_brand_template_response_instance = GetBrandTemplateResponse.from_json(json)
# print the JSON string representation of the object
print(GetBrandTemplateResponse.to_json())

# convert the object into a dict
get_brand_template_response_dict = get_brand_template_response_instance.to_dict()
# create an instance of GetBrandTemplateResponse from a dict
get_brand_template_response_from_dict = GetBrandTemplateResponse.from_dict(get_brand_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


