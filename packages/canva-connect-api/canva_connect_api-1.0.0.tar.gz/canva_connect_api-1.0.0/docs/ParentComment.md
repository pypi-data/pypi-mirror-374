# ParentComment

Data about the comment, including the message, author, and the object (such as a design) the comment is attached to.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**id** | **str** | The ID of the comment.  You can use this ID to create replies to the comment using the [Create reply API](https://www.canva.dev/docs/connect/api-reference/comments/create-reply/). | 
**attached_to** | [**DesignCommentObject**](DesignCommentObject.md) |  | [optional] 
**message** | **str** | The comment message. This is the comment body shown in the Canva UI. User mentions are shown here in the format &#x60;[user_id:team_id]&#x60;. | 
**author** | [**User**](User.md) |  | 
**created_at** | **int** | When the comment or reply was created, as a Unix timestamp (in seconds since the Unix Epoch). | [optional] 
**updated_at** | **int** | When the comment or reply was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | [optional] 
**mentions** | [**Dict[str, TeamUser]**](TeamUser.md) | The Canva users mentioned in the comment. | 
**assignee** | [**User**](User.md) |  | [optional] 
**resolver** | [**User**](User.md) |  | [optional] 

## Example

```python
from openapi_client.models.parent_comment import ParentComment

# TODO update the JSON string below
json = "{}"
# create an instance of ParentComment from a JSON string
parent_comment_instance = ParentComment.from_json(json)
# print the JSON string representation of the object
print(ParentComment.to_json())

# convert the object into a dict
parent_comment_dict = parent_comment_instance.to_dict()
# create an instance of ParentComment from a dict
parent_comment_from_dict = ParentComment.from_dict(parent_comment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


