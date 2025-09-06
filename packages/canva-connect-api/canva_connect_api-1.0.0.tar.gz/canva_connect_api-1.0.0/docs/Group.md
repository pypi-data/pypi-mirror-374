# Group

Metadata for the Canva Group, consisting of the Group ID, display name, and whether it's an external Canva Group.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the group with permissions to access the design. | 
**display_name** | **str** | The display name of the group. | [optional] 
**external** | **bool** | Is the user making the API call (the authenticated user) and the Canva Group from different Canva Teams?  - When &#x60;true&#x60;, the user and the group aren&#39;t in the same Canva Team. - When &#x60;false&#x60;, the user and the group are in the same Canva Team. | 

## Example

```python
from openapi_client.models.group import Group

# TODO update the JSON string below
json = "{}"
# create an instance of Group from a JSON string
group_instance = Group.from_json(json)
# print the JSON string representation of the object
print(Group.to_json())

# convert the object into a dict
group_dict = group_instance.to_dict()
# create an instance of Group from a dict
group_from_dict = Group.from_dict(group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


