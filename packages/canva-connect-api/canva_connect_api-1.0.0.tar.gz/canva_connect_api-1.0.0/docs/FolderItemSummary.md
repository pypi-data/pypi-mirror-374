# FolderItemSummary

Details about the folder item.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**folder** | [**Folder**](Folder.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**image** | [**AssetSummary**](AssetSummary.md) |  | 

## Example

```python
from openapi_client.models.folder_item_summary import FolderItemSummary

# TODO update the JSON string below
json = "{}"
# create an instance of FolderItemSummary from a JSON string
folder_item_summary_instance = FolderItemSummary.from_json(json)
# print the JSON string representation of the object
print(FolderItemSummary.to_json())

# convert the object into a dict
folder_item_summary_dict = folder_item_summary_instance.to_dict()
# create an instance of FolderItemSummary from a dict
folder_item_summary_from_dict = FolderItemSummary.from_dict(folder_item_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


