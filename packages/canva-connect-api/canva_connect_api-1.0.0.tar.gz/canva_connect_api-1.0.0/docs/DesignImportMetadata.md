# DesignImportMetadata

Metadata about the design that you include as a header parameter when importing a design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title_base64** | **str** | The design&#39;s title, encoded in Base64.  The maximum length of a design title in Canva (unencoded) is 50 characters.  Base64 encoding allows titles containing emojis and other special characters to be sent using HTTP headers. For example, \&quot;My Awesome Design 😍\&quot; Base64 encoded is &#x60;TXkgQXdlc29tZSBEZXNpZ24g8J+YjQ&#x3D;&#x3D;&#x60;. | 
**mime_type** | **str** | The MIME type of the file being imported. If not provided, Canva attempts to automatically detect the type of the file. | [optional] 

## Example

```python
from openapi_client.models.design_import_metadata import DesignImportMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of DesignImportMetadata from a JSON string
design_import_metadata_instance = DesignImportMetadata.from_json(json)
# print the JSON string representation of the object
print(DesignImportMetadata.to_json())

# convert the object into a dict
design_import_metadata_dict = design_import_metadata_instance.to_dict()
# create an instance of DesignImportMetadata from a dict
design_import_metadata_from_dict = DesignImportMetadata.from_dict(design_import_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


