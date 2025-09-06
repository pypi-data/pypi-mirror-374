# FormatSuggestedEdit

A suggestion to format some text.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**format** | [**SuggestionFormat**](SuggestionFormat.md) |  | 

## Example

```python
from openapi_client.models.format_suggested_edit import FormatSuggestedEdit

# TODO update the JSON string below
json = "{}"
# create an instance of FormatSuggestedEdit from a JSON string
format_suggested_edit_instance = FormatSuggestedEdit.from_json(json)
# print the JSON string representation of the object
print(FormatSuggestedEdit.to_json())

# convert the object into a dict
format_suggested_edit_dict = format_suggested_edit_instance.to_dict()
# create an instance of FormatSuggestedEdit from a dict
format_suggested_edit_from_dict = FormatSuggestedEdit.from_dict(format_suggested_edit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


