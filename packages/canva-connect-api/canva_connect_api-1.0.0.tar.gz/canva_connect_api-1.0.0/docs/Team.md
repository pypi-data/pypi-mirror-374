# Team

Metadata for the Canva Team, consisting of the Team ID, display name, and whether it's an external Canva Team.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the Canva Team. | 
**display_name** | **str** | The name of the Canva Team as shown in the Canva UI. | 
**external** | **bool** | Is the user making the API call (the authenticated user) from the Canva Team shown?  - When &#x60;true&#x60;, the user isn&#39;t in the Canva Team shown. - When &#x60;false&#x60;, the user is in the Canva Team shown. | 

## Example

```python
from openapi_client.models.team import Team

# TODO update the JSON string below
json = "{}"
# create an instance of Team from a JSON string
team_instance = Team.from_json(json)
# print the JSON string representation of the object
print(Team.to_json())

# convert the object into a dict
team_dict = team_instance.to_dict()
# create an instance of Team from a dict
team_from_dict = Team.from_dict(team_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


