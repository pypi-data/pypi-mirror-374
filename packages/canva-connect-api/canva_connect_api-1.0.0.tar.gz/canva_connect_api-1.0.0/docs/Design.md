# Design

The design object, which contains metadata about the design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The design ID. | 
**title** | **str** | The design title. | [optional] 
**owner** | [**TeamUserSummary**](TeamUserSummary.md) |  | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | [optional] 
**urls** | [**DesignLinks**](DesignLinks.md) |  | 
**created_at** | **int** | When the design was created in Canva, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the design was last updated in Canva, as a Unix timestamp (in seconds since the Unix Epoch). | 
**page_count** | **int** | The total number of pages in the design. Some design types don&#39;t have pages (for example, Canva docs). | [optional] 

## Example

```python
from openapi_client.models.design import Design

# TODO update the JSON string below
json = "{}"
# create an instance of Design from a JSON string
design_instance = Design.from_json(json)
# print the JSON string representation of the object
print(Design.to_json())

# convert the object into a dict
design_dict = design_instance.to_dict()
# create an instance of Design from a dict
design_from_dict = Design.from_dict(design_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


