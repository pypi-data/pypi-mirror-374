# ReplyCommentEvent

Event type for a reply to a comment thread.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**reply_url** | **str** | A URL to the design, focused on the comment reply. | 
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.reply_comment_event import ReplyCommentEvent

# TODO update the JSON string below
json = "{}"
# create an instance of ReplyCommentEvent from a JSON string
reply_comment_event_instance = ReplyCommentEvent.from_json(json)
# print the JSON string representation of the object
print(ReplyCommentEvent.to_json())

# convert the object into a dict
reply_comment_event_dict = reply_comment_event_instance.to_dict()
# create an instance of ReplyCommentEvent from a dict
reply_comment_event_from_dict = ReplyCommentEvent.from_dict(reply_comment_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


