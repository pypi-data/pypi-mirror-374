# TeamUser

Metadata for the user, consisting of the User ID, Team ID, and display name.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the user. | [optional] 
**team_id** | **str** | The ID of the user&#39;s Canva Team. | [optional] 
**display_name** | **str** | The name of the user as shown in the Canva UI. | [optional] 

## Example

```python
from openapi_client.models.team_user import TeamUser

# TODO update the JSON string below
json = "{}"
# create an instance of TeamUser from a JSON string
team_user_instance = TeamUser.from_json(json)
# print the JSON string representation of the object
print(TeamUser.to_json())

# convert the object into a dict
team_user_dict = team_user_instance.to_dict()
# create an instance of TeamUser from a dict
team_user_from_dict = TeamUser.from_dict(team_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


