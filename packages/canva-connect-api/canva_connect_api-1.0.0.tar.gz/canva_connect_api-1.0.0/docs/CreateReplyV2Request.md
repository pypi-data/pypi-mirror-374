# CreateReplyV2Request


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_plaintext** | **str** | The comment message of the reply in plaintext. This is the reply comment shown in the Canva UI.  You can also mention users in your message by specifying their User ID and Team ID using the format &#x60;[user_id:team_id]&#x60;. | 

## Example

```python
from openapi_client.models.create_reply_v2_request import CreateReplyV2Request

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReplyV2Request from a JSON string
create_reply_v2_request_instance = CreateReplyV2Request.from_json(json)
# print the JSON string representation of the object
print(CreateReplyV2Request.to_json())

# convert the object into a dict
create_reply_v2_request_dict = create_reply_v2_request_instance.to_dict()
# create an instance of CreateReplyV2Request from a dict
create_reply_v2_request_from_dict = CreateReplyV2Request.from_dict(create_reply_v2_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


