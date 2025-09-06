# GetDesignPagesResponse

Successful response from a `getDesignPages` request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[DesignPage]**](DesignPage.md) | The list of pages. | 

## Example

```python
from openapi_client.models.get_design_pages_response import GetDesignPagesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDesignPagesResponse from a JSON string
get_design_pages_response_instance = GetDesignPagesResponse.from_json(json)
# print the JSON string representation of the object
print(GetDesignPagesResponse.to_json())

# convert the object into a dict
get_design_pages_response_dict = get_design_pages_response_instance.to_dict()
# create an instance of GetDesignPagesResponse from a dict
get_design_pages_response_from_dict = GetDesignPagesResponse.from_dict(get_design_pages_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


