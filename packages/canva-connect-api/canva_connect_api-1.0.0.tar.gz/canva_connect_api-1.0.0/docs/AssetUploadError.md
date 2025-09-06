# AssetUploadError

If the upload fails, this object provides details about the error.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | [**AssetUploadErrorCode**](AssetUploadErrorCode.md) |  | 
**message** | **str** | A human-readable description of what went wrong. | 

## Example

```python
from openapi_client.models.asset_upload_error import AssetUploadError

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadError from a JSON string
asset_upload_error_instance = AssetUploadError.from_json(json)
# print the JSON string representation of the object
print(AssetUploadError.to_json())

# convert the object into a dict
asset_upload_error_dict = asset_upload_error_instance.to_dict()
# create an instance of AssetUploadError from a dict
asset_upload_error_from_dict = AssetUploadError.from_dict(asset_upload_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


