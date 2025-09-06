# AutofillError

If the autofill job fails, this object provides details about the error.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | [**AutofillErrorCode**](AutofillErrorCode.md) |  | 
**message** | **str** | A human-readable description of what went wrong. | 

## Example

```python
from openapi_client.models.autofill_error import AutofillError

# TODO update the JSON string below
json = "{}"
# create an instance of AutofillError from a JSON string
autofill_error_instance = AutofillError.from_json(json)
# print the JSON string representation of the object
print(AutofillError.to_json())

# convert the object into a dict
autofill_error_dict = autofill_error_instance.to_dict()
# create an instance of AutofillError from a dict
autofill_error_from_dict = AutofillError.from_dict(autofill_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


