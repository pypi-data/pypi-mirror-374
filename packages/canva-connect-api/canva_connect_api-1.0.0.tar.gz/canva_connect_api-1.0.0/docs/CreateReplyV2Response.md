# CreateReplyV2Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.create_reply_v2_response import CreateReplyV2Response

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReplyV2Response from a JSON string
create_reply_v2_response_instance = CreateReplyV2Response.from_json(json)
# print the JSON string representation of the object
print(CreateReplyV2Response.to_json())

# convert the object into a dict
create_reply_v2_response_dict = create_reply_v2_response_instance.to_dict()
# create an instance of CreateReplyV2Response from a dict
create_reply_v2_response_from_dict = CreateReplyV2Response.from_dict(create_reply_v2_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


