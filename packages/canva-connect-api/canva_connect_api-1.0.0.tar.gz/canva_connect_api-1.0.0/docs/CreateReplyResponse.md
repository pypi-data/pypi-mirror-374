# CreateReplyResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | [**ReplyComment**](ReplyComment.md) |  | 

## Example

```python
from openapi_client.models.create_reply_response import CreateReplyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReplyResponse from a JSON string
create_reply_response_instance = CreateReplyResponse.from_json(json)
# print the JSON string representation of the object
print(CreateReplyResponse.to_json())

# convert the object into a dict
create_reply_response_dict = create_reply_response_instance.to_dict()
# create an instance of CreateReplyResponse from a dict
create_reply_response_from_dict = CreateReplyResponse.from_dict(create_reply_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


