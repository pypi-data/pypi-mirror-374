# GetReplyResponse

Successful response from a `getReply` request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.get_reply_response import GetReplyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetReplyResponse from a JSON string
get_reply_response_instance = GetReplyResponse.from_json(json)
# print the JSON string representation of the object
print(GetReplyResponse.to_json())

# convert the object into a dict
get_reply_response_dict = get_reply_response_instance.to_dict()
# create an instance of GetReplyResponse from a dict
get_reply_response_from_dict = GetReplyResponse.from_dict(get_reply_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


