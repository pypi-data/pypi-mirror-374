# ShareDesignNotificationContent

The notification content for when someone shares a design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**share_url** | **str** | A URL that the user who receives the notification can use to access the shared design. | 
**share** | [**ShareAction**](ShareAction.md) |  | [optional] 

## Example

```python
from openapi_client.models.share_design_notification_content import ShareDesignNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of ShareDesignNotificationContent from a JSON string
share_design_notification_content_instance = ShareDesignNotificationContent.from_json(json)
# print the JSON string representation of the object
print(ShareDesignNotificationContent.to_json())

# convert the object into a dict
share_design_notification_content_dict = share_design_notification_content_instance.to_dict()
# create an instance of ShareDesignNotificationContent from a dict
share_design_notification_content_from_dict = ShareDesignNotificationContent.from_dict(share_design_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


