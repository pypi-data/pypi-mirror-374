# GetBrandTemplateDatasetResponse

Successful response from a `getBrandTemplateDataset` request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset** | [**Dict[str, DataField]**](DataField.md) | The dataset definition for the brand template. The dataset definition contains the data inputs available for use with the [Create design autofill job API](https://www.canva.dev/docs/connect/api-reference/autofills/create-design-autofill-job/). | [optional] 

## Example

```python
from openapi_client.models.get_brand_template_dataset_response import GetBrandTemplateDatasetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBrandTemplateDatasetResponse from a JSON string
get_brand_template_dataset_response_instance = GetBrandTemplateDatasetResponse.from_json(json)
# print the JSON string representation of the object
print(GetBrandTemplateDatasetResponse.to_json())

# convert the object into a dict
get_brand_template_dataset_response_dict = get_brand_template_dataset_response_instance.to_dict()
# create an instance of GetBrandTemplateDatasetResponse from a dict
get_brand_template_dataset_response_from_dict = GetBrandTemplateDatasetResponse.from_dict(get_brand_template_dataset_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


