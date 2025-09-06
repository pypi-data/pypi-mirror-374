# ExportError

If the export fails, this object provides details about the error.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | [**ExportErrorCode**](ExportErrorCode.md) |  | 
**message** | **str** | A human-readable description of what went wrong. | 

## Example

```python
from openapi_client.models.export_error import ExportError

# TODO update the JSON string below
json = "{}"
# create an instance of ExportError from a JSON string
export_error_instance = ExportError.from_json(json)
# print the JSON string representation of the object
print(ExportError.to_json())

# convert the object into a dict
export_error_dict = export_error_instance.to_dict()
# create an instance of ExportError from a dict
export_error_from_dict = ExportError.from_dict(export_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


