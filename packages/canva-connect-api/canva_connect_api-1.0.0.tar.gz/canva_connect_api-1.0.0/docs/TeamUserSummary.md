# TeamUserSummary

Metadata for the user, consisting of the User ID and Team ID.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The ID of the user. | 
**team_id** | **str** | The ID of the user&#39;s Canva Team. | 

## Example

```python
from openapi_client.models.team_user_summary import TeamUserSummary

# TODO update the JSON string below
json = "{}"
# create an instance of TeamUserSummary from a JSON string
team_user_summary_instance = TeamUserSummary.from_json(json)
# print the JSON string representation of the object
print(TeamUserSummary.to_json())

# convert the object into a dict
team_user_summary_dict = team_user_summary_instance.to_dict()
# create an instance of TeamUserSummary from a dict
team_user_summary_from_dict = TeamUserSummary.from_dict(team_user_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


