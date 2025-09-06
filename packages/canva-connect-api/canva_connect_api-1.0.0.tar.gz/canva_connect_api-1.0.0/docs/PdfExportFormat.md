# PdfExportFormat

Export the design as a PDF. Providing a paper size is optional.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**export_quality** | [**ExportQuality**](ExportQuality.md) |  | [optional] [default to ExportQuality.REGULAR]
**size** | [**ExportPageSize**](ExportPageSize.md) |  | [optional] [default to ExportPageSize.A4]
**pages** | **List[int]** | To specify which pages to export in a multi-page design, provide the page numbers as an array. The first page in a design is page &#x60;1&#x60;. If &#x60;pages&#x60; isn&#39;t specified, all the pages are exported. | [optional] 

## Example

```python
from openapi_client.models.pdf_export_format import PdfExportFormat

# TODO update the JSON string below
json = "{}"
# create an instance of PdfExportFormat from a JSON string
pdf_export_format_instance = PdfExportFormat.from_json(json)
# print the JSON string representation of the object
print(PdfExportFormat.to_json())

# convert the object into a dict
pdf_export_format_dict = pdf_export_format_instance.to_dict()
# create an instance of PdfExportFormat from a dict
pdf_export_format_from_dict = PdfExportFormat.from_dict(pdf_export_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


