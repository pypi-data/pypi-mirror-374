# CreateFolderResponse

Details about the new folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**folder** | [**Folder**](Folder.md) |  | [optional] 

## Example

```python
from openapi_client.models.create_folder_response import CreateFolderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFolderResponse from a JSON string
create_folder_response_instance = CreateFolderResponse.from_json(json)
# print the JSON string representation of the object
print(CreateFolderResponse.to_json())

# convert the object into a dict
create_folder_response_dict = create_folder_response_instance.to_dict()
# create an instance of CreateFolderResponse from a dict
create_folder_response_from_dict = CreateFolderResponse.from_dict(create_folder_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


