# ThreadMentionEventContent

Content for a mention in a comment thread.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**comment_url** | **str** | A URL to the design, focused on the comment thread. | 
**comment** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.thread_mention_event_content import ThreadMentionEventContent

# TODO update the JSON string below
json = "{}"
# create an instance of ThreadMentionEventContent from a JSON string
thread_mention_event_content_instance = ThreadMentionEventContent.from_json(json)
# print the JSON string representation of the object
print(ThreadMentionEventContent.to_json())

# convert the object into a dict
thread_mention_event_content_dict = thread_mention_event_content_instance.to_dict()
# create an instance of ThreadMentionEventContent from a dict
thread_mention_event_content_from_dict = ThreadMentionEventContent.from_dict(thread_mention_event_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


