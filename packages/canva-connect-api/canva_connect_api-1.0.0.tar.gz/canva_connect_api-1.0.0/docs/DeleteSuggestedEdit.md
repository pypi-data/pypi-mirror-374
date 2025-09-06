# DeleteSuggestedEdit

A suggestion to delete some text.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**text** | **str** |  | 

## Example

```python
from openapi_client.models.delete_suggested_edit import DeleteSuggestedEdit

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteSuggestedEdit from a JSON string
delete_suggested_edit_instance = DeleteSuggestedEdit.from_json(json)
# print the JSON string representation of the object
print(DeleteSuggestedEdit.to_json())

# convert the object into a dict
delete_suggested_edit_dict = delete_suggested_edit_instance.to_dict()
# create an instance of DeleteSuggestedEdit from a dict
delete_suggested_edit_from_dict = DeleteSuggestedEdit.from_dict(delete_suggested_edit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


