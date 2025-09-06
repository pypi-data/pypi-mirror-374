# Reply

A reply to a thread.  The `author` of the reply might be missing if that user account no longer exists.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the reply. | 
**design_id** | **str** | The ID of the design that the thread for this reply is attached to. | 
**thread_id** | **str** | The ID of the thread this reply is in. | 
**author** | [**User**](User.md) |  | [optional] 
**content** | [**CommentContent**](CommentContent.md) |  | 
**mentions** | [**Dict[str, UserMention]**](UserMention.md) | The Canva users mentioned in the comment thread or reply. | 
**created_at** | **int** | When the reply was created, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the reply was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | 

## Example

```python
from openapi_client.models.reply import Reply

# TODO update the JSON string below
json = "{}"
# create an instance of Reply from a JSON string
reply_instance = Reply.from_json(json)
# print the JSON string representation of the object
print(Reply.to_json())

# convert the object into a dict
reply_dict = reply_instance.to_dict()
# create an instance of Reply from a dict
reply_from_dict = Reply.from_dict(reply_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


