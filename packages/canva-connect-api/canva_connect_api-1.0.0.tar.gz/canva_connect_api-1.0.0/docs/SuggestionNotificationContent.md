# SuggestionNotificationContent

The notification content when someone does one of the following actions:   - Suggests edits to a design.  - Applies or rejects a suggestion.  - Replies to a suggestion.  - Mentions a user in a reply to a suggestion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**triggering_user** | [**User**](User.md) |  | 
**receiving_team_user** | [**TeamUser**](TeamUser.md) |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 
**suggestion_event_type** | [**SuggestionEventType**](SuggestionEventType.md) |  | 

## Example

```python
from openapi_client.models.suggestion_notification_content import SuggestionNotificationContent

# TODO update the JSON string below
json = "{}"
# create an instance of SuggestionNotificationContent from a JSON string
suggestion_notification_content_instance = SuggestionNotificationContent.from_json(json)
# print the JSON string representation of the object
print(SuggestionNotificationContent.to_json())

# convert the object into a dict
suggestion_notification_content_dict = suggestion_notification_content_instance.to_dict()
# create an instance of SuggestionNotificationContent from a dict
suggestion_notification_content_from_dict = SuggestionNotificationContent.from_dict(suggestion_notification_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


