# AssetUploadMetadata

Metadata for the asset being uploaded.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name_base64** | **str** | The asset&#39;s name, encoded in Base64.  The maximum length of an asset name in Canva (unencoded) is 50 characters.  Base64 encoding allows names containing emojis and other special characters to be sent using HTTP headers. For example, \&quot;My Awesome Upload 🚀\&quot; Base64 encoded is &#x60;TXkgQXdlc29tZSBVcGxvYWQg8J+agA&#x3D;&#x3D;&#x60;. | 

## Example

```python
from openapi_client.models.asset_upload_metadata import AssetUploadMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadMetadata from a JSON string
asset_upload_metadata_instance = AssetUploadMetadata.from_json(json)
# print the JSON string representation of the object
print(AssetUploadMetadata.to_json())

# convert the object into a dict
asset_upload_metadata_dict = asset_upload_metadata_instance.to_dict()
# create an instance of AssetUploadMetadata from a dict
asset_upload_metadata_from_dict = AssetUploadMetadata.from_dict(asset_upload_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


