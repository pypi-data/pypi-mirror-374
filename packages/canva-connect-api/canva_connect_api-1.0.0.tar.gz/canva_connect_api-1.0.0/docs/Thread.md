# Thread

A discussion thread on a design.  The `type` of the thread can be found in the `thread_type` object, along with additional type-specific properties. The `author` of the thread might be missing if that user account no longer exists.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the thread.  You can use this ID to create replies to the thread using the [Create reply API](https://www.canva.dev/docs/connect/api-reference/comments/create-reply/). | 
**design_id** | **str** | The ID of the design that the discussion thread is on. | 
**thread_type** | [**ThreadType**](ThreadType.md) |  | 
**author** | [**User**](User.md) |  | [optional] 
**created_at** | **int** | When the thread was created, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the thread was last updated, as a Unix timestamp (in seconds since the Unix Epoch). | 

## Example

```python
from openapi_client.models.thread import Thread

# TODO update the JSON string below
json = "{}"
# create an instance of Thread from a JSON string
thread_instance = Thread.from_json(json)
# print the JSON string representation of the object
print(Thread.to_json())

# convert the object into a dict
thread_dict = thread_instance.to_dict()
# create an instance of Thread from a dict
thread_from_dict = Thread.from_dict(thread_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


