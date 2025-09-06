# DesignMentionNotificationContent

The notification content for when someone mentions a user in a design.  The link to the design in this notification is valid for 30 days, and can only be opened by the recipient of the notification.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 

## Example

```python
from openapi_client.models.design_mention_notification_content import DesignMentionNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of DesignMentionNotificationContent from a JSON string
design_mention_notification_content_instance = DesignMentionNotificationContent.from_json(json)
# print the JSON string representation of the object
print(DesignMentionNotificationContent.to_json())

# convert the object into a dict
design_mention_notification_content_dict = design_mention_notification_content_instance.to_dict()
# create an instance of DesignMentionNotificationContent from a dict
design_mention_notification_content_from_dict = DesignMentionNotificationContent.from_dict(design_mention_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


