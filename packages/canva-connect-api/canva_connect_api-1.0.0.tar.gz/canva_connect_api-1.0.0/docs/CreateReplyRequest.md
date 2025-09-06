# CreateReplyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attached_to** | [**DesignCommentObjectInput**](DesignCommentObjectInput.md) |  | 
**message** | **str** | The reply comment message. This is the reply comment body shown in the Canva UI.  You can also mention users in your message by specifying their User ID and Team ID using the format &#x60;[user_id:team_id]&#x60;. | 

## Example

```python
from openapi_client.models.create_reply_request import CreateReplyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReplyRequest from a JSON string
create_reply_request_instance = CreateReplyRequest.from_json(json)
# print the JSON string representation of the object
print(CreateReplyRequest.to_json())

# convert the object into a dict
create_reply_request_dict = create_reply_request_instance.to_dict()
# create an instance of CreateReplyRequest from a dict
create_reply_request_from_dict = CreateReplyRequest.from_dict(create_reply_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


