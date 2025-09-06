# Comment

The comment object, which contains metadata about the comment. Deprecated in favor of the new `thread` object.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **str** | The ID of the comment. | 
**attached_to** | [**DesignCommentObject**](DesignCommentObject.md) |  | [optional] 
**message** | **str** | The comment message. This is the comment body shown in the Canva UI. User mentions are shown here in the format &#x60;[user_id:team_id]&#x60;. | 
**author** | [**User**](User.md) |  | 
**created_at** | **int** | When the comment or reply was created, as a Unix timestamp (in seconds since the Unix Epoch). | [optional] 
**updated_at** | **int** | When the comment or reply was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | [optional] 
**mentions** | [**Dict[str, TeamUser]**](TeamUser.md) | The Canva users mentioned in the comment. | 
**assignee** | [**User**](User.md) |  | [optional] 
**resolver** | [**User**](User.md) |  | [optional] 
**thread_id** | **str** | The ID of the comment thread this reply is in. This ID is the same as the &#x60;id&#x60; of the parent comment. | 

## Example

```python
from openapi_client.models.comment import Comment

# TODO update the JSON string below
json = "{}"
# create an instance of Comment from a JSON string
comment_instance = Comment.from_json(json)
# print the JSON string representation of the object
print(Comment.to_json())

# convert the object into a dict
comment_dict = comment_instance.to_dict()
# create an instance of Comment from a dict
comment_from_dict = Comment.from_dict(comment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


