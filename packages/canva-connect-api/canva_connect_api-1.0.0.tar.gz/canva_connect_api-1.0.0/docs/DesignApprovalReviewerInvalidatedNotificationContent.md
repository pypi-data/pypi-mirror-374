# DesignApprovalReviewerInvalidatedNotificationContent

The notification content for when a reviewer in a design is invalidated.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**receiving_team_user** | [**TeamUserSummary**](TeamUserSummary.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 

## Example

```python
from openapi_client.models.design_approval_reviewer_invalidated_notification_content import DesignApprovalReviewerInvalidatedNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of DesignApprovalReviewerInvalidatedNotificationContent from a JSON string
design_approval_reviewer_invalidated_notification_content_instance = DesignApprovalReviewerInvalidatedNotificationContent.from_json(json)
# print the JSON string representation of the object
print(DesignApprovalReviewerInvalidatedNotificationContent.to_json())

# convert the object into a dict
design_approval_reviewer_invalidated_notification_content_dict = design_approval_reviewer_invalidated_notification_content_instance.to_dict()
# create an instance of DesignApprovalReviewerInvalidatedNotificationContent from a dict
design_approval_reviewer_invalidated_notification_content_from_dict = DesignApprovalReviewerInvalidatedNotificationContent.from_dict(design_approval_reviewer_invalidated_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


