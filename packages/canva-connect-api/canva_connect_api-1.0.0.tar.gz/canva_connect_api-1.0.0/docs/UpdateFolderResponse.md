# UpdateFolderResponse

Details about the updated folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**folder** | [**Folder**](Folder.md) |  | [optional] 

## Example

```python
from openapi_client.models.update_folder_response import UpdateFolderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateFolderResponse from a JSON string
update_folder_response_instance = UpdateFolderResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateFolderResponse.to_json())

# convert the object into a dict
update_folder_response_dict = update_folder_response_instance.to_dict()
# create an instance of UpdateFolderResponse from a dict
update_folder_response_from_dict = UpdateFolderResponse.from_dict(update_folder_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


