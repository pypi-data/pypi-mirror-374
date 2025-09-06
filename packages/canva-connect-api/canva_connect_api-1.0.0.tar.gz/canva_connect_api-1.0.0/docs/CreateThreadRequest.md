# CreateThreadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_plaintext** | **str** | The comment message in plaintext. This is the comment body shown in the Canva UI.  You can also mention users in your message by specifying their User ID and Team ID using the format &#x60;[user_id:team_id]&#x60;. If the &#x60;assignee_id&#x60; parameter is specified, you must mention the assignee in the message. | 
**assignee_id** | **str** | Lets you assign the comment to a Canva user using their User ID. You _must_ mention the assigned user in the &#x60;message&#x60;. | [optional] 

## Example

```python
from openapi_client.models.create_thread_request import CreateThreadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateThreadRequest from a JSON string
create_thread_request_instance = CreateThreadRequest.from_json(json)
# print the JSON string representation of the object
print(CreateThreadRequest.to_json())

# convert the object into a dict
create_thread_request_dict = create_thread_request_instance.to_dict()
# create an instance of CreateThreadRequest from a dict
create_thread_request_from_dict = CreateThreadRequest.from_dict(create_thread_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


