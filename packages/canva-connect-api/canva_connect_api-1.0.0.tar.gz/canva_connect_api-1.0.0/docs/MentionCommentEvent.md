# MentionCommentEvent

Event type for a mention in a comment thread or reply.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**content** | [**MentionEventContent**](MentionEventContent.md) |  | 

## Example

```python
from openapi_client.models.mention_comment_event import MentionCommentEvent

# TODO update the JSON string below
json = "{}"
# create an instance of MentionCommentEvent from a JSON string
mention_comment_event_instance = MentionCommentEvent.from_json(json)
# print the JSON string representation of the object
print(MentionCommentEvent.to_json())

# convert the object into a dict
mention_comment_event_dict = mention_comment_event_instance.to_dict()
# create an instance of MentionCommentEvent from a dict
mention_comment_event_from_dict = MentionCommentEvent.from_dict(mention_comment_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


