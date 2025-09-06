# MentionSuggestionEventType

Event type for a mention in a reply to a suggestion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**reply_url** | **str** | A URL to the design, focused on the suggestion reply. | 
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.mention_suggestion_event_type import MentionSuggestionEventType

# TODO update the JSON string below
json = "{}"
# create an instance of MentionSuggestionEventType from a JSON string
mention_suggestion_event_type_instance = MentionSuggestionEventType.from_json(json)
# print the JSON string representation of the object
print(MentionSuggestionEventType.to_json())

# convert the object into a dict
mention_suggestion_event_type_dict = mention_suggestion_event_type_instance.to_dict()
# create an instance of MentionSuggestionEventType from a dict
mention_suggestion_event_type_from_dict = MentionSuggestionEventType.from_dict(mention_suggestion_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


