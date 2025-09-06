# ExportFormatOptions

The available file formats for exporting the design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pdf** | **object** | Whether the design can be exported as a PDF. | [optional] 
**jpg** | **object** | Whether the design can be exported as a JPEG. | [optional] 
**png** | **object** | Whether the design can be exported as a PNG. | [optional] 
**svg** | **object** | Whether the design can be exported as an SVG. | [optional] 
**pptx** | **object** | Whether the design can be exported as a PPTX. | [optional] 
**gif** | **object** | Whether the design can be exported as a GIF. | [optional] 
**mp4** | **object** | Whether the design can be exported as an MP4. | [optional] 

## Example

```python
from openapi_client.models.export_format_options import ExportFormatOptions

# TODO update the JSON string below
json = "{}"
# create an instance of ExportFormatOptions from a JSON string
export_format_options_instance = ExportFormatOptions.from_json(json)
# print the JSON string representation of the object
print(ExportFormatOptions.to_json())

# convert the object into a dict
export_format_options_dict = export_format_options_instance.to_dict()
# create an instance of ExportFormatOptions from a dict
export_format_options_from_dict = ExportFormatOptions.from_dict(export_format_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


