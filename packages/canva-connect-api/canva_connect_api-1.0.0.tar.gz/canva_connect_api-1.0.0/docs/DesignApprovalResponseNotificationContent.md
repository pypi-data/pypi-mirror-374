# DesignApprovalResponseNotificationContent

The notification content for when someone approves a design or gives feedback.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**initial_requesting_user** | [**TeamUser**](TeamUser.md) |  | 
**responding_groups** | [**List[Group]**](Group.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**approval_response** | [**ApprovalResponseAction**](ApprovalResponseAction.md) |  | 

## Example

```python
from openapi_client.models.design_approval_response_notification_content import DesignApprovalResponseNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of DesignApprovalResponseNotificationContent from a JSON string
design_approval_response_notification_content_instance = DesignApprovalResponseNotificationContent.from_json(json)
# print the JSON string representation of the object
print(DesignApprovalResponseNotificationContent.to_json())

# convert the object into a dict
design_approval_response_notification_content_dict = design_approval_response_notification_content_instance.to_dict()
# create an instance of DesignApprovalResponseNotificationContent from a dict
design_approval_response_notification_content_from_dict = DesignApprovalResponseNotificationContent.from_dict(design_approval_response_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


