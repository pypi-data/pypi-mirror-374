# AssignedCommentEvent

Event type for a comment thread that has been assigned.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**comment_url** | **str** | A URL to the design, focused on the comment thread. | 
**comment** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.assigned_comment_event import AssignedCommentEvent

# TODO update the JSON string below
json = "{}"
# create an instance of AssignedCommentEvent from a JSON string
assigned_comment_event_instance = AssignedCommentEvent.from_json(json)
# print the JSON string representation of the object
print(AssignedCommentEvent.to_json())

# convert the object into a dict
assigned_comment_event_dict = assigned_comment_event_instance.to_dict()
# create an instance of AssignedCommentEvent from a dict
assigned_comment_event_from_dict = AssignedCommentEvent.from_dict(assigned_comment_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


