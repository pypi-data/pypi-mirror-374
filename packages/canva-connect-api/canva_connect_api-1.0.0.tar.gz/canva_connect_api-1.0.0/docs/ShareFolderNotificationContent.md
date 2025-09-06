# ShareFolderNotificationContent

The notification content for when someone shares a folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**folder** | [**FolderSummary**](FolderSummary.md) |  | 
**share** | [**ShareAction**](ShareAction.md) |  | [optional] 

## Example

```python
from openapi_client.models.share_folder_notification_content import ShareFolderNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of ShareFolderNotificationContent from a JSON string
share_folder_notification_content_instance = ShareFolderNotificationContent.from_json(json)
# print the JSON string representation of the object
print(ShareFolderNotificationContent.to_json())

# convert the object into a dict
share_folder_notification_content_dict = share_folder_notification_content_instance.to_dict()
# create an instance of ShareFolderNotificationContent from a dict
share_folder_notification_content_from_dict = ShareFolderNotificationContent.from_dict(share_folder_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


