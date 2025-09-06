# ShareAction

Metadata about the share event.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | The optional message users can include when sharing something with another user using the Canva UI. | 

## Example

```python
from openapi_client.models.share_action import ShareAction

# TODO update the JSON string below
json = "{}"
# create an instance of ShareAction from a JSON string
share_action_instance = ShareAction.from_json(json)
# print the JSON string representation of the object
print(ShareAction.to_json())

# convert the object into a dict
share_action_dict = share_action_instance.to_dict()
# create an instance of ShareAction from a dict
share_action_from_dict = ShareAction.from_dict(share_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


