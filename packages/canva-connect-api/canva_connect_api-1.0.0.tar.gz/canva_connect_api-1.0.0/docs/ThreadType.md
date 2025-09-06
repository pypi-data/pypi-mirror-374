# ThreadType

The type of the discussion thread, along with additional type-specific properties.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**content** | [**CommentContent**](CommentContent.md) |  | 
**mentions** | [**Dict[str, UserMention]**](UserMention.md) | The Canva users mentioned in the comment thread or reply. | 
**assignee** | [**User**](User.md) |  | [optional] 
**resolver** | [**User**](User.md) |  | [optional] 
**suggested_edits** | [**List[SuggestedEdit]**](SuggestedEdit.md) |  | 
**status** | [**SuggestionStatus**](SuggestionStatus.md) |  | 

## Example

```python
from openapi_client.models.thread_type import ThreadType

# TODO update the JSON string below
json = "{}"
# create an instance of ThreadType from a JSON string
thread_type_instance = ThreadType.from_json(json)
# print the JSON string representation of the object
print(ThreadType.to_json())

# convert the object into a dict
thread_type_dict = thread_type_instance.to_dict()
# create an instance of ThreadType from a dict
thread_type_from_dict = ThreadType.from_dict(thread_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


