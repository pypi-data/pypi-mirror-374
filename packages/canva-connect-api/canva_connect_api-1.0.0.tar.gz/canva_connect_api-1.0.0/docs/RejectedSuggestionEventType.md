# RejectedSuggestionEventType

Event type for a suggestion that has been rejected.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**suggestion_url** | **str** | A URL to the design, focused on the suggestion. | 
**suggestion** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.rejected_suggestion_event_type import RejectedSuggestionEventType

# TODO update the JSON string below
json = "{}"
# create an instance of RejectedSuggestionEventType from a JSON string
rejected_suggestion_event_type_instance = RejectedSuggestionEventType.from_json(json)
# print the JSON string representation of the object
print(RejectedSuggestionEventType.to_json())

# convert the object into a dict
rejected_suggestion_event_type_dict = rejected_suggestion_event_type_instance.to_dict()
# create an instance of RejectedSuggestionEventType from a dict
rejected_suggestion_event_type_from_dict = RejectedSuggestionEventType.from_dict(rejected_suggestion_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


