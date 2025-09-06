# FolderAccessRequestedNotificationContent

The notification content for when someone requests access to a folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**TeamUser**](TeamUser.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**folder** | [**FolderSummary**](FolderSummary.md) |  | 

## Example

```python
from openapi_client.models.folder_access_requested_notification_content import FolderAccessRequestedNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of FolderAccessRequestedNotificationContent from a JSON string
folder_access_requested_notification_content_instance = FolderAccessRequestedNotificationContent.from_json(json)
# print the JSON string representation of the object
print(FolderAccessRequestedNotificationContent.to_json())

# convert the object into a dict
folder_access_requested_notification_content_dict = folder_access_requested_notification_content_instance.to_dict()
# create an instance of FolderAccessRequestedNotificationContent from a dict
folder_access_requested_notification_content_from_dict = FolderAccessRequestedNotificationContent.from_dict(folder_access_requested_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


