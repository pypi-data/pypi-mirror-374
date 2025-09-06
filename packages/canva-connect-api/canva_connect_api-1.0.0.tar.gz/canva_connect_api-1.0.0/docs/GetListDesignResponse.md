# GetListDesignResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**continuation** | **str** | A continuation token. If the success response contains a continuation token, the list contains more designs you can list. You can use this token as a query parameter and retrieve more designs from the list, for example &#x60;/v1/designs?continuation&#x3D;{continuation}&#x60;.  To retrieve all of a user&#39;s designs, you might need to make multiple requests. | [optional] 
**items** | [**List[Design]**](Design.md) | The list of designs. | 

## Example

```python
from openapi_client.models.get_list_design_response import GetListDesignResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetListDesignResponse from a JSON string
get_list_design_response_instance = GetListDesignResponse.from_json(json)
# print the JSON string representation of the object
print(GetListDesignResponse.to_json())

# convert the object into a dict
get_list_design_response_dict = get_list_design_response_instance.to_dict()
# create an instance of GetListDesignResponse from a dict
get_list_design_response_from_dict = GetListDesignResponse.from_dict(get_list_design_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


