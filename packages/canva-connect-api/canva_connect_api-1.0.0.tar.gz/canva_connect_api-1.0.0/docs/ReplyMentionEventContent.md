# ReplyMentionEventContent

Content for a mention in a comment reply.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**reply_url** | **str** | A URL to the design, focused on the comment reply. | 
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.reply_mention_event_content import ReplyMentionEventContent

# TODO update the JSON string below
json = "{}"
# create an instance of ReplyMentionEventContent from a JSON string
reply_mention_event_content_instance = ReplyMentionEventContent.from_json(json)
# print the JSON string representation of the object
print(ReplyMentionEventContent.to_json())

# convert the object into a dict
reply_mention_event_content_dict = reply_mention_event_content_instance.to_dict()
# create an instance of ReplyMentionEventContent from a dict
reply_mention_event_content_from_dict = ReplyMentionEventContent.from_dict(reply_mention_event_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


