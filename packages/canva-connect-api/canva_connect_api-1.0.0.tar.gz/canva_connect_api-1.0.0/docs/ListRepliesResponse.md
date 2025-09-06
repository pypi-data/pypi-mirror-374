# ListRepliesResponse

Successful response from a `listReplies` request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**continuation** | **str** | If the success response contains a continuation token, the list contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example &#x60;?continuation&#x3D;{continuation}&#x60;.  To retrieve all items, you might need to make multiple requests. | [optional] 
**items** | [**List[Reply]**](Reply.md) |  | 

## Example

```python
from openapi_client.models.list_replies_response import ListRepliesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListRepliesResponse from a JSON string
list_replies_response_instance = ListRepliesResponse.from_json(json)
# print the JSON string representation of the object
print(ListRepliesResponse.to_json())

# convert the object into a dict
list_replies_response_dict = list_replies_response_instance.to_dict()
# create an instance of ListRepliesResponse from a dict
list_replies_response_from_dict = ListRepliesResponse.from_dict(list_replies_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


