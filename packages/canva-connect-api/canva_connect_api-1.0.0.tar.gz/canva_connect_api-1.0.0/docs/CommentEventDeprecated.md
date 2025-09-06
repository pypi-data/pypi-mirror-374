# CommentEventDeprecated

Basic details about the comment.  The `comment` property is deprecated. For details of the comment event, use the `comment_event` property instead.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**CommentEventTypeEnum**](CommentEventTypeEnum.md) |  | 
**data** | [**Comment**](Comment.md) |  | 

## Example

```python
from openapi_client.models.comment_event_deprecated import CommentEventDeprecated

# TODO update the JSON string below
json = "{}"
# create an instance of CommentEventDeprecated from a JSON string
comment_event_deprecated_instance = CommentEventDeprecated.from_json(json)
# print the JSON string representation of the object
print(CommentEventDeprecated.to_json())

# convert the object into a dict
comment_event_deprecated_dict = comment_event_deprecated_instance.to_dict()
# create an instance of CommentEventDeprecated from a dict
comment_event_deprecated_from_dict = CommentEventDeprecated.from_dict(comment_event_deprecated_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


