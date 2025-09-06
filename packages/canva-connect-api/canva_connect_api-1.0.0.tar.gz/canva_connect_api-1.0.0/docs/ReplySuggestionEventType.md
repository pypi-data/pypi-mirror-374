# ReplySuggestionEventType

Event type for a reply to a suggestion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**reply_url** | **str** | A URL to the design, focused on the suggestion reply. | 
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.reply_suggestion_event_type import ReplySuggestionEventType

# TODO update the JSON string below
json = "{}"
# create an instance of ReplySuggestionEventType from a JSON string
reply_suggestion_event_type_instance = ReplySuggestionEventType.from_json(json)
# print the JSON string representation of the object
print(ReplySuggestionEventType.to_json())

# convert the object into a dict
reply_suggestion_event_type_dict = reply_suggestion_event_type_instance.to_dict()
# create an instance of ReplySuggestionEventType from a dict
reply_suggestion_event_type_from_dict = ReplySuggestionEventType.from_dict(reply_suggestion_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


