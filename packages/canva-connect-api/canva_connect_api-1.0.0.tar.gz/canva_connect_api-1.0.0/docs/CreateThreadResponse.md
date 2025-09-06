# CreateThreadResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**thread** | [**Thread**](Thread.md) |  | 

## Example

```python
from openapi_client.models.create_thread_response import CreateThreadResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateThreadResponse from a JSON string
create_thread_response_instance = CreateThreadResponse.from_json(json)
# print the JSON string representation of the object
print(CreateThreadResponse.to_json())

# convert the object into a dict
create_thread_response_dict = create_thread_response_instance.to_dict()
# create an instance of CreateThreadResponse from a dict
create_thread_response_from_dict = CreateThreadResponse.from_dict(create_thread_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


