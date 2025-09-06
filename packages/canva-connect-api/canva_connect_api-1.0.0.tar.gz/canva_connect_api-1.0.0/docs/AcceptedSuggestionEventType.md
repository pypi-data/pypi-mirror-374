# AcceptedSuggestionEventType

Event type for a suggestion that has been accepted.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**suggestion_url** | **str** | A URL to the design, focused on the suggestion. | 
**suggestion** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.accepted_suggestion_event_type import AcceptedSuggestionEventType

# TODO update the JSON string below
json = "{}"
# create an instance of AcceptedSuggestionEventType from a JSON string
accepted_suggestion_event_type_instance = AcceptedSuggestionEventType.from_json(json)
# print the JSON string representation of the object
print(AcceptedSuggestionEventType.to_json())

# convert the object into a dict
accepted_suggestion_event_type_dict = accepted_suggestion_event_type_instance.to_dict()
# create an instance of AcceptedSuggestionEventType from a dict
accepted_suggestion_event_type_from_dict = AcceptedSuggestionEventType.from_dict(accepted_suggestion_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


