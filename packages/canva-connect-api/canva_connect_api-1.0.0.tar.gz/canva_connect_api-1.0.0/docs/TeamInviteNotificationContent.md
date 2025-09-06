# TeamInviteNotificationContent

The notification content for when someone is invited to a [Canva team](https://www.canva.com/help/about-canva-for-teams/).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_user** | [**User**](User.md) |  | 
**inviting_team** | [**Team**](Team.md) |  | 

## Example

```python
from openapi_client.models.team_invite_notification_content import TeamInviteNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of TeamInviteNotificationContent from a JSON string
team_invite_notification_content_instance = TeamInviteNotificationContent.from_json(json)
# print the JSON string representation of the object
print(TeamInviteNotificationContent.to_json())

# convert the object into a dict
team_invite_notification_content_dict = team_invite_notification_content_instance.to_dict()
# create an instance of TeamInviteNotificationContent from a dict
team_invite_notification_content_from_dict = TeamInviteNotificationContent.from_dict(team_invite_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


