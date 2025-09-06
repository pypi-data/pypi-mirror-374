# NotificationContent

The notification content object, which contains metadata about the event.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**share_url** | **str** | A URL that the user who receives the notification can use to access the shared design. | 
**share** | [**ShareAction**](ShareAction.md) |  | [optional] 
**folder** | [**FolderSummary**](FolderSummary.md) |  | 
**comment_url** | **str** | A URL to the design, focused on the new comment.  The &#x60;comment_url&#x60; property is deprecated. For details of the comment event, use the &#x60;comment_event&#x60; property instead. | [optional] 
**comment** | [**CommentEventDeprecated**](CommentEventDeprecated.md) |  | [optional] 
**comment_event** | [**CommentEvent**](CommentEvent.md) |  | [optional] 
**grant_access_url** | **str** | A URL, which is scoped only to the user that can grant the requested access to the design, that approves the requested access. | 
**initial_requesting_user** | [**TeamUser**](TeamUser.md) |  | 
**requested_groups** | [**List[Group]**](Group.md) |  | 
**approve_url** | **str** | A URL, which is scoped only to the user requested to review the design, that links to the design with the approval UI opened. | 
**approval_request** | [**ApprovalRequestAction**](ApprovalRequestAction.md) |  | 
**responding_groups** | [**List[Group]**](Group.md) |  | 
**approval_response** | [**ApprovalResponseAction**](ApprovalResponseAction.md) |  | 
**receiving_user** | [**User**](User.md) |  | 
**inviting_team** | [**Team**](Team.md) |  | 
**suggestion_event_type** | [**SuggestionEventType**](SuggestionEventType.md) |  | 

## Example

```python
from openapi_client.models.notification_content import NotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationContent from a JSON string
notification_content_instance = NotificationContent.from_json(json)
# print the JSON string representation of the object
print(NotificationContent.to_json())

# convert the object into a dict
notification_content_dict = notification_content_instance.to_dict()
# create an instance of NotificationContent from a dict
notification_content_from_dict = NotificationContent.from_dict(notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


