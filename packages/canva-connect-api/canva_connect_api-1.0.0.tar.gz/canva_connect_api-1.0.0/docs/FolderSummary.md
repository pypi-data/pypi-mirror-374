# FolderSummary

This object contains some folder metadata. You can retrieve additional metadata using the folder ID and the `/v1/folders/{folderId}` endpoint.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The folder ID. | 
**title** | **str** | The folder name, as shown in the Canva UI. This property is deprecated, so you should use the &#x60;name&#x60; property instead. | [optional] 
**name** | **str** | The folder name, as shown in the Canva UI. | 
**created_at** | **int** | When the folder was created, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the folder was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | 
**url** | **str** | The folder URL. | [optional] 

## Example

```python
from openapi_client.models.folder_summary import FolderSummary

# TODO update the JSON string below
json = "{}"
# create an instance of FolderSummary from a JSON string
folder_summary_instance = FolderSummary.from_json(json)
# print the JSON string representation of the object
print(FolderSummary.to_json())

# convert the object into a dict
folder_summary_dict = folder_summary_instance.to_dict()
# create an instance of FolderSummary from a dict
folder_summary_from_dict = FolderSummary.from_dict(folder_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


