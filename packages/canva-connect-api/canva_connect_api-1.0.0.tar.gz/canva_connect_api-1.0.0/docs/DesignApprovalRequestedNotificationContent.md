# DesignApprovalRequestedNotificationContent

The notification content for when someone requests a user to [approve a design](https://www.canva.com/help/get-approval/).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**initial_requesting_user** | [**TeamUser**](TeamUser.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**requested_groups** | [**List[Group]**](Group.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**approve_url** | **str** | A URL, which is scoped only to the user requested to review the design, that links to the design with the approval UI opened. | 
**approval_request** | [**ApprovalRequestAction**](ApprovalRequestAction.md) |  | 

## Example

```python
from openapi_client.models.design_approval_requested_notification_content import DesignApprovalRequestedNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of DesignApprovalRequestedNotificationContent from a JSON string
design_approval_requested_notification_content_instance = DesignApprovalRequestedNotificationContent.from_json(json)
# print the JSON string representation of the object
print(DesignApprovalRequestedNotificationContent.to_json())

# convert the object into a dict
design_approval_requested_notification_content_dict = design_approval_requested_notification_content_instance.to_dict()
# create an instance of DesignApprovalRequestedNotificationContent from a dict
design_approval_requested_notification_content_from_dict = DesignApprovalRequestedNotificationContent.from_dict(design_approval_requested_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


