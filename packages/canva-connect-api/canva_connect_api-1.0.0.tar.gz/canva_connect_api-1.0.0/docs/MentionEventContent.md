# MentionEventContent

The type of mention event content, along with additional type-specific properties.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**comment_url** | **str** | A URL to the design, focused on the comment thread. | 
**comment** | [**Thread**](Thread.md) |  | 
**reply_url** | **str** | A URL to the design, focused on the comment reply. | 
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.mention_event_content import MentionEventContent

# TODO update the JSON string below
json = "{}"
# create an instance of MentionEventContent from a JSON string
mention_event_content_instance = MentionEventContent.from_json(json)
# print the JSON string representation of the object
print(MentionEventContent.to_json())

# convert the object into a dict
mention_event_content_dict = mention_event_content_instance.to_dict()
# create an instance of MentionEventContent from a dict
mention_event_content_from_dict = MentionEventContent.from_dict(mention_event_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


