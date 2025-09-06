# CommentContent

The content of a comment thread or reply.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plaintext** | **str** | The content in plaintext. Any user mention tags are shown in the format &#x60;[user_id:team_id]&#x60;. | 
**markdown** | **str** | The content in markdown. Any user mention tags are shown in the format &#x60;[user_id:team_id]&#x60; | [optional] 

## Example

```python
from openapi_client.models.comment_content import CommentContent

# TODO update the JSON string below
json = "{}"
# create an instance of CommentContent from a JSON string
comment_content_instance = CommentContent.from_json(json)
# print the JSON string representation of the object
print(CommentContent.to_json())

# convert the object into a dict
comment_content_dict = comment_content_instance.to_dict()
# create an instance of CommentContent from a dict
comment_content_from_dict = CommentContent.from_dict(comment_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


