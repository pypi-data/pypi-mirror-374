# CommentNotificationContent

The notification content for when someone comments on a design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**comment_url** | **str** | A URL to the design, focused on the new comment.  The &#x60;comment_url&#x60; property is deprecated. For details of the comment event, use the &#x60;comment_event&#x60; property instead. | [optional] 
**comment** | [**CommentEventDeprecated**](CommentEventDeprecated.md) |  | [optional] 
**comment_event** | [**CommentEvent**](CommentEvent.md) |  | [optional] 

## Example

```python
from openapi_client.models.comment_notification_content import CommentNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of CommentNotificationContent from a JSON string
comment_notification_content_instance = CommentNotificationContent.from_json(json)
# print the JSON string representation of the object
print(CommentNotificationContent.to_json())

# convert the object into a dict
comment_notification_content_dict = comment_notification_content_instance.to_dict()
# create an instance of CommentNotificationContent from a dict
comment_notification_content_from_dict = CommentNotificationContent.from_dict(comment_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


