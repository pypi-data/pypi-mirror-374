# MoveFolderItemRequest

Body parameters for moving the folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**to_folder_id** | **str** | The ID of the folder you want to move the item to (the destination folder). If you want to move the item to the top level of a Canva user&#39;s [projects](https://www.canva.com/help/find-designs-and-folders/), use the ID &#x60;root&#x60;. | 
**item_id** | **str** | The ID of the item you want to move. Currently, video assets are not supported. | 

## Example

```python
from openapi_client.models.move_folder_item_request import MoveFolderItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MoveFolderItemRequest from a JSON string
move_folder_item_request_instance = MoveFolderItemRequest.from_json(json)
# print the JSON string representation of the object
print(MoveFolderItemRequest.to_json())

# convert the object into a dict
move_folder_item_request_dict = move_folder_item_request_instance.to_dict()
# create an instance of MoveFolderItemRequest from a dict
move_folder_item_request_from_dict = MoveFolderItemRequest.from_dict(move_folder_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


