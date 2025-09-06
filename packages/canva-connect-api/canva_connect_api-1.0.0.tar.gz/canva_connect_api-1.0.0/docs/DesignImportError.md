# DesignImportError

If the import job fails, this object provides details about the error.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | [**DesignImportErrorCode**](DesignImportErrorCode.md) |  | 
**message** | **str** | A human-readable description of what went wrong. | 

## Example

```python
from openapi_client.models.design_import_error import DesignImportError

# TODO update the JSON string below
json = "{}"
# create an instance of DesignImportError from a JSON string
design_import_error_instance = DesignImportError.from_json(json)
# print the JSON string representation of the object
print(DesignImportError.to_json())

# convert the object into a dict
design_import_error_dict = design_import_error_instance.to_dict()
# create an instance of DesignImportError from a dict
design_import_error_from_dict = DesignImportError.from_dict(design_import_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


