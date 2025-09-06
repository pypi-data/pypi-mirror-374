# ApprovalRequestAction

Metadata about the design approval request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | The message included by the user when requesting a design approval. | [optional] 

## Example

```python
from openapi_client.models.approval_request_action import ApprovalRequestAction

# TODO update the JSON string below
json = "{}"
# create an instance of ApprovalRequestAction from a JSON string
approval_request_action_instance = ApprovalRequestAction.from_json(json)
# print the JSON string representation of the object
print(ApprovalRequestAction.to_json())

# convert the object into a dict
approval_request_action_dict = approval_request_action_instance.to_dict()
# create an instance of ApprovalRequestAction from a dict
approval_request_action_from_dict = ApprovalRequestAction.from_dict(approval_request_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


