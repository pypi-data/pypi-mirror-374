# DesignResizeError

If the design resize job fails, this object provides details about the error.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | [**DesignResizeErrorCode**](DesignResizeErrorCode.md) |  | 
**message** | **str** | A human-readable description of what went wrong. | 

## Example

```python
from openapi_client.models.design_resize_error import DesignResizeError

# TODO update the JSON string below
json = "{}"
# create an instance of DesignResizeError from a JSON string
design_resize_error_instance = DesignResizeError.from_json(json)
# print the JSON string representation of the object
print(DesignResizeError.to_json())

# convert the object into a dict
design_resize_error_dict = design_resize_error_instance.to_dict()
# create an instance of DesignResizeError from a dict
design_resize_error_from_dict = DesignResizeError.from_dict(design_resize_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


