# PptxExportFormat

Export the design as a PPTX.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**pages** | **List[int]** | To specify which pages to export in a multi-page design, provide the page numbers as an array. The first page in a design is page &#x60;1&#x60;. If &#x60;pages&#x60; isn&#39;t specified, all the pages are exported. | [optional] 

## Example

```python
from openapi_client.models.pptx_export_format import PptxExportFormat

# TODO update the JSON string below
json = "{}"
# create an instance of PptxExportFormat from a JSON string
pptx_export_format_instance = PptxExportFormat.from_json(json)
# print the JSON string representation of the object
print(PptxExportFormat.to_json())

# convert the object into a dict
pptx_export_format_dict = pptx_export_format_instance.to_dict()
# create an instance of PptxExportFormat from a dict
pptx_export_format_from_dict = PptxExportFormat.from_dict(pptx_export_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


