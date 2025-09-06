# CreateFolderRequest

Body parameters for creating a new folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the folder. | 
**parent_folder_id** | **str** | The folder ID of the parent folder. To create a new folder at the top level of a user&#39;s [projects](https://www.canva.com/help/find-designs-and-folders/), use the ID &#x60;root&#x60;. To create it in their Uploads folder, use &#x60;uploads&#x60;. | 

## Example

```python
from openapi_client.models.create_folder_request import CreateFolderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFolderRequest from a JSON string
create_folder_request_instance = CreateFolderRequest.from_json(json)
# print the JSON string representation of the object
print(CreateFolderRequest.to_json())

# convert the object into a dict
create_folder_request_dict = create_folder_request_instance.to_dict()
# create an instance of CreateFolderRequest from a dict
create_folder_request_from_dict = CreateFolderRequest.from_dict(create_folder_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


