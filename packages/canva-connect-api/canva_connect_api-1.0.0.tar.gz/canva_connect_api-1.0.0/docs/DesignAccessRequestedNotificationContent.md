# DesignAccessRequestedNotificationContent

The notification content for when someone requests access to a design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**TeamUser**](TeamUser.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**grant_access_url** | **str** | A URL, which is scoped only to the user that can grant the requested access to the design, that approves the requested access. | 

## Example

```python
from openapi_client.models.design_access_requested_notification_content import DesignAccessRequestedNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of DesignAccessRequestedNotificationContent from a JSON string
design_access_requested_notification_content_instance = DesignAccessRequestedNotificationContent.from_json(json)
# print the JSON string representation of the object
print(DesignAccessRequestedNotificationContent.to_json())

# convert the object into a dict
design_access_requested_notification_content_dict = design_access_requested_notification_content_instance.to_dict()
# create an instance of DesignAccessRequestedNotificationContent from a dict
design_access_requested_notification_content_from_dict = DesignAccessRequestedNotificationContent.from_dict(design_access_requested_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


