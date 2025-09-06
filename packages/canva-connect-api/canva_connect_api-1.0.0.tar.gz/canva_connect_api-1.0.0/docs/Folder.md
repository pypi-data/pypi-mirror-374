# Folder

The folder object, which contains metadata about the folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The folder ID. | 
**name** | **str** | The folder name. | 
**created_at** | **int** | When the folder was created, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the folder was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | [optional] 

## Example

```python
from openapi_client.models.folder import Folder

# TODO update the JSON string below
json = "{}"
# create an instance of Folder from a JSON string
folder_instance = Folder.from_json(json)
# print the JSON string representation of the object
print(Folder.to_json())

# convert the object into a dict
folder_dict = folder_instance.to_dict()
# create an instance of Folder from a dict
folder_from_dict = Folder.from_dict(folder_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


