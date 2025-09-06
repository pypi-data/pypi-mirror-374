# FolderItem

Details about the folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**folder** | [**Folder**](Folder.md) |  | 

## Example

```python
from openapi_client.models.folder_item import FolderItem

# TODO update the JSON string below
json = "{}"
# create an instance of FolderItem from a JSON string
folder_item_instance = FolderItem.from_json(json)
# print the JSON string representation of the object
print(FolderItem.to_json())

# convert the object into a dict
folder_item_dict = folder_item_instance.to_dict()
# create an instance of FolderItem from a dict
folder_item_from_dict = FolderItem.from_dict(folder_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


