# ListFolderItemsResponse

A list of the items in a folder. If the success response contains a continuation token, the folder contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example `/v1/folders/{folderId}/items?continuation={continuation}`.  To retrieve all the items in a folder, you might need to make multiple requests.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[FolderItemSummary]**](FolderItemSummary.md) | An array of items in the folder. | 
**continuation** | **str** | If the success response contains a continuation token, the folder contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example &#x60;/v1/folders/{folderId}/items?continuation&#x3D;{continuation}&#x60;.  To retrieve all the items in a folder, you might need to make multiple requests. | [optional] 

## Example

```python
from openapi_client.models.list_folder_items_response import ListFolderItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListFolderItemsResponse from a JSON string
list_folder_items_response_instance = ListFolderItemsResponse.from_json(json)
# print the JSON string representation of the object
print(ListFolderItemsResponse.to_json())

# convert the object into a dict
list_folder_items_response_dict = list_folder_items_response_instance.to_dict()
# create an instance of ListFolderItemsResponse from a dict
list_folder_items_response_from_dict = ListFolderItemsResponse.from_dict(list_folder_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


