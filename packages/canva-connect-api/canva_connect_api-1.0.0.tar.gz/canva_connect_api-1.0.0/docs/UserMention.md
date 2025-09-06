# UserMention

Information about the user mentioned in a comment thread or reply. Each user mention is keyed using the user's user ID and team ID separated by a colon (`user_id:team_id`).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tag** | **str** | The mention tag for the user mentioned in the comment thread or reply content. This has the format of the user&#39;s user ID and team ID separated by a colon (&#x60;user_id:team_id&#x60;). | 
**user** | [**TeamUser**](TeamUser.md) |  | 

## Example

```python
from openapi_client.models.user_mention import UserMention

# TODO update the JSON string below
json = "{}"
# create an instance of UserMention from a JSON string
user_mention_instance = UserMention.from_json(json)
# print the JSON string representation of the object
print(UserMention.to_json())

# convert the object into a dict
user_mention_dict = user_mention_instance.to_dict()
# create an instance of UserMention from a dict
user_mention_from_dict = UserMention.from_dict(user_mention_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


