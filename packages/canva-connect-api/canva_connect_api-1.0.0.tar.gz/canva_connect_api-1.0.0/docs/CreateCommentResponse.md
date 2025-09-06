# CreateCommentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | [**ParentComment**](ParentComment.md) |  | 

## Example

```python
from openapi_client.models.create_comment_response import CreateCommentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCommentResponse from a JSON string
create_comment_response_instance = CreateCommentResponse.from_json(json)
# print the JSON string representation of the object
print(CreateCommentResponse.to_json())

# convert the object into a dict
create_comment_response_dict = create_comment_response_instance.to_dict()
# create an instance of CreateCommentResponse from a dict
create_comment_response_from_dict = CreateCommentResponse.from_dict(create_comment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


