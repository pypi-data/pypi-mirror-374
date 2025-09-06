# ApprovalResponseAction

Metadata about the design approval response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**approved** | **bool** | Whether the design was approved. When &#x60;true&#x60;, the reviewer has approved the design. | 
**ready_to_publish** | **bool** | Whether the design is ready to publish. When &#x60;true&#x60;, the design has been approved by all reviewers and can be published. | [optional] 
**message** | **str** | The message included by a user responding to a design approval request. | [optional] 

## Example

```python
from openapi_client.models.approval_response_action import ApprovalResponseAction

# TODO update the JSON string below
json = "{}"
# create an instance of ApprovalResponseAction from a JSON string
approval_response_action_instance = ApprovalResponseAction.from_json(json)
# print the JSON string representation of the object
print(ApprovalResponseAction.to_json())

# convert the object into a dict
approval_response_action_dict = approval_response_action_instance.to_dict()
# create an instance of ApprovalResponseAction from a dict
approval_response_action_from_dict = ApprovalResponseAction.from_dict(approval_response_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


