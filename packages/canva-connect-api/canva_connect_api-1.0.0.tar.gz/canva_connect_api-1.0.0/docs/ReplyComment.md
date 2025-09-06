# ReplyComment

Data about the reply comment, including the message, author, and the object (such as a design) the comment is attached to.

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
**thread_id** | **str** | The ID of the comment thread this reply is in. This ID is the same as the &#x60;id&#x60; of the parent comment. | 

## Example

```python
from openapi_client.models.reply_comment import ReplyComment

# TODO update the JSON string below
json = "{}"
# create an instance of ReplyComment from a JSON string
reply_comment_instance = ReplyComment.from_json(json)
# print the JSON string representation of the object
print(ReplyComment.to_json())

# convert the object into a dict
reply_comment_dict = reply_comment_instance.to_dict()
# create an instance of ReplyComment from a dict
reply_comment_from_dict = ReplyComment.from_dict(reply_comment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


