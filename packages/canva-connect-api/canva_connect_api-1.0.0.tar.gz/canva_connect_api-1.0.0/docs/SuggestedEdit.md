# SuggestedEdit

The type of the suggested edit, along with additional type-specific properties.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**text** | **str** |  | 
**format** | [**SuggestionFormat**](SuggestionFormat.md) |  | 

## Example

```python
from openapi_client.models.suggested_edit import SuggestedEdit

# TODO update the JSON string below
json = "{}"
# create an instance of SuggestedEdit from a JSON string
suggested_edit_instance = SuggestedEdit.from_json(json)
# print the JSON string representation of the object
print(SuggestedEdit.to_json())

# convert the object into a dict
suggested_edit_dict = suggested_edit_instance.to_dict()
# create an instance of SuggestedEdit from a dict
suggested_edit_from_dict = SuggestedEdit.from_dict(suggested_edit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


