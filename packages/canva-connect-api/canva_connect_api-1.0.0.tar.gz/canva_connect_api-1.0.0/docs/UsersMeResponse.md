# UsersMeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_user** | [**TeamUserSummary**](TeamUserSummary.md) |  | 

## Example

```python
from openapi_client.models.users_me_response import UsersMeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UsersMeResponse from a JSON string
users_me_response_instance = UsersMeResponse.from_json(json)
# print the JSON string representation of the object
print(UsersMeResponse.to_json())

# convert the object into a dict
users_me_response_dict = users_me_response_instance.to_dict()
# create an instance of UsersMeResponse from a dict
users_me_response_from_dict = UsersMeResponse.from_dict(users_me_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


