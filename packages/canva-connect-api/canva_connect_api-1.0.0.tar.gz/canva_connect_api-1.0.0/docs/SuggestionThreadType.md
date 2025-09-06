# SuggestionThreadType

A suggestion thread.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**suggested_edits** | [**List[SuggestedEdit]**](SuggestedEdit.md) |  | 
**status** | [**SuggestionStatus**](SuggestionStatus.md) |  | 

## Example

```python
from openapi_client.models.suggestion_thread_type import SuggestionThreadType

# TODO update the JSON string below
json = "{}"
# create an instance of SuggestionThreadType from a JSON string
suggestion_thread_type_instance = SuggestionThreadType.from_json(json)
# print the JSON string representation of the object
print(SuggestionThreadType.to_json())

# convert the object into a dict
suggestion_thread_type_dict = suggestion_thread_type_instance.to_dict()
# create an instance of SuggestionThreadType from a dict
suggestion_thread_type_from_dict = SuggestionThreadType.from_dict(suggestion_thread_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


