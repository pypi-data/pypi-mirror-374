# DesignPage

Basic details about a page in a design, such as the page's index and thumbnail.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** | The index of the page in the design. The first page in a design has the index value &#x60;1&#x60;. | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | [optional] 

## Example

```python
from openapi_client.models.design_page import DesignPage

# TODO update the JSON string below
json = "{}"
# create an instance of DesignPage from a JSON string
design_page_instance = DesignPage.from_json(json)
# print the JSON string representation of the object
print(DesignPage.to_json())

# convert the object into a dict
design_page_dict = design_page_instance.to_dict()
# create an instance of DesignPage from a dict
design_page_from_dict = DesignPage.from_dict(design_page_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


