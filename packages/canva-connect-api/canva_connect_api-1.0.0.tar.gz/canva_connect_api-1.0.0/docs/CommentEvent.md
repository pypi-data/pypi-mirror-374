# CommentEvent

The type of comment event, including additional type-specific properties.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**comment_url** | **str** | A URL to the design, focused on the comment thread. | 
**comment** | [**Thread**](Thread.md) |  | 
**reply_url** | **str** | A URL to the design, focused on the comment reply. | 
**reply** | [**Reply**](Reply.md) |  | 
**content** | [**MentionEventContent**](MentionEventContent.md) |  | 

## Example

```python
from openapi_client.models.comment_event import CommentEvent

# TODO update the JSON string below
json = "{}"
# create an instance of CommentEvent from a JSON string
comment_event_instance = CommentEvent.from_json(json)
# print the JSON string representation of the object
print(CommentEvent.to_json())

# convert the object into a dict
comment_event_dict = comment_event_instance.to_dict()
# create an instance of CommentEvent from a dict
comment_event_from_dict = CommentEvent.from_dict(comment_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


