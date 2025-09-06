# NewSuggestionEventType

Event type for a new suggestion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**suggestion_url** | **str** | A URL to the design, focused on the suggestion. | 
**suggestion** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.new_suggestion_event_type import NewSuggestionEventType

# TODO update the JSON string below
json = "{}"
# create an instance of NewSuggestionEventType from a JSON string
new_suggestion_event_type_instance = NewSuggestionEventType.from_json(json)
# print the JSON string representation of the object
print(NewSuggestionEventType.to_json())

# convert the object into a dict
new_suggestion_event_type_dict = new_suggestion_event_type_instance.to_dict()
# create an instance of NewSuggestionEventType from a dict
new_suggestion_event_type_from_dict = NewSuggestionEventType.from_dict(new_suggestion_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


