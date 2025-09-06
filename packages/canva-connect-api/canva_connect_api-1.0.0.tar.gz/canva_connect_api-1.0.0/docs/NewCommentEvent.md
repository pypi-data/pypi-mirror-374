# NewCommentEvent

Event type for a new comment thread.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**comment_url** | **str** | A URL to the design, focused on the comment thread. | 
**comment** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.new_comment_event import NewCommentEvent

# TODO update the JSON string below
json = "{}"
# create an instance of NewCommentEvent from a JSON string
new_comment_event_instance = NewCommentEvent.from_json(json)
# print the JSON string representation of the object
print(NewCommentEvent.to_json())

# convert the object into a dict
new_comment_event_dict = new_comment_event_instance.to_dict()
# create an instance of NewCommentEvent from a dict
new_comment_event_from_dict = NewCommentEvent.from_dict(new_comment_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


