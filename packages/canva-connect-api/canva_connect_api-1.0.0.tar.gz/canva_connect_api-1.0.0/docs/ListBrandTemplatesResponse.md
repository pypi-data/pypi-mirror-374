# ListBrandTemplatesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**continuation** | **str** | If the success response contains a continuation token, the user has access to more brand templates you can list. You can use this token as a query parameter and retrieve more templates from the list, for example &#x60;/v1/brand-templates?continuation&#x3D;{continuation}&#x60;. To retrieve all the brand templates available to the user, you might need to make multiple requests. | [optional] 
**items** | [**List[BrandTemplate]**](BrandTemplate.md) | The list of brand templates. | 

## Example

```python
from openapi_client.models.list_brand_templates_response import ListBrandTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListBrandTemplatesResponse from a JSON string
list_brand_templates_response_instance = ListBrandTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(ListBrandTemplatesResponse.to_json())

# convert the object into a dict
list_brand_templates_response_dict = list_brand_templates_response_instance.to_dict()
# create an instance of ListBrandTemplatesResponse from a dict
list_brand_templates_response_from_dict = ListBrandTemplatesResponse.from_dict(list_brand_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


