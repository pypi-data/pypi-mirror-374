# SuggestionEventType

The type of suggestion event, along with additional type-specific properties.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**suggestion_url** | **str** | A URL to the design, focused on the suggestion. | 
**suggestion** | [**Thread**](Thread.md) |  | 
**reply_url** | **str** | A URL to the design, focused on the suggestion reply. | 
**reply** | [**Reply**](Reply.md) |  | 

## Example

```python
from openapi_client.models.suggestion_event_type import SuggestionEventType

# TODO update the JSON string below
json = "{}"
# create an instance of SuggestionEventType from a JSON string
suggestion_event_type_instance = SuggestionEventType.from_json(json)
# print the JSON string representation of the object
print(SuggestionEventType.to_json())

# convert the object into a dict
suggestion_event_type_dict = suggestion_event_type_instance.to_dict()
# create an instance of SuggestionEventType from a dict
suggestion_event_type_from_dict = SuggestionEventType.from_dict(suggestion_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


