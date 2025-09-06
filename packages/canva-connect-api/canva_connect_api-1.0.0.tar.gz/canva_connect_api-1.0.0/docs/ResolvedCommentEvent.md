# ResolvedCommentEvent

Event type for a comment thread that has been resolved.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**comment_url** | **str** | A URL to the design, focused on the comment thread. | 
**comment** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.resolved_comment_event import ResolvedCommentEvent

# TODO update the JSON string below
json = "{}"
# create an instance of ResolvedCommentEvent from a JSON string
resolved_comment_event_instance = ResolvedCommentEvent.from_json(json)
# print the JSON string representation of the object
print(ResolvedCommentEvent.to_json())

# convert the object into a dict
resolved_comment_event_dict = resolved_comment_event_instance.to_dict()
# create an instance of ResolvedCommentEvent from a dict
resolved_comment_event_from_dict = ResolvedCommentEvent.from_dict(resolved_comment_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


