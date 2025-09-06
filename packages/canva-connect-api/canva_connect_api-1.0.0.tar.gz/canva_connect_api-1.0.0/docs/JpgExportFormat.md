# JpgExportFormat

Export the design as a JPEG. Compression quality must be provided. Height or width (or both) may be specified, otherwise the file will be exported at it's default size.  If the user is on the Canva Free plan, the export height and width for a fixed-dimension design can't be upscaled by more than a factor of `1.125`.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**export_quality** | [**ExportQuality**](ExportQuality.md) |  | [optional] [default to ExportQuality.REGULAR]
**quality** | **int** | For the &#x60;jpg&#x60; type, the &#x60;quality&#x60; of the exported JPEG determines how compressed the exported file should be. A _low_ &#x60;quality&#x60; value will create a file with a smaller file size, but the resulting file will have pixelated artifacts when compared to a file created with a _high_ &#x60;quality&#x60; value. | 
**height** | **int** | Specify the height in pixels of the exported image. Note the following behavior:  - If no height or width is specified, the image is exported using the dimensions of the design. - If only one of height or width is specified, then the image is scaled to match that dimension, respecting the design&#39;s aspect ratio. - If both the height and width are specified, but the values don&#39;t match the design&#39;s aspect ratio, the export defaults to the larger dimension. | [optional] 
**width** | **int** | Specify the width in pixels of the exported image. Note the following behavior:  - If no width or height is specified, the image is exported using the dimensions of the design. - If only one of width or height is specified, then the image is scaled to match that dimension, respecting the design&#39;s aspect ratio. - If both the width and height are specified, but the values don&#39;t match the design&#39;s aspect ratio, the export defaults to the larger dimension. | [optional] 
**pages** | **List[int]** | To specify which pages to export in a multi-page design, provide the page numbers as an array. The first page in a design is page &#x60;1&#x60;. If &#x60;pages&#x60; isn&#39;t specified, all the pages are exported. | [optional] 

## Example

```python
from openapi_client.models.jpg_export_format import JpgExportFormat

# TODO update the JSON string below
json = "{}"
# create an instance of JpgExportFormat from a JSON string
jpg_export_format_instance = JpgExportFormat.from_json(json)
# print the JSON string representation of the object
print(JpgExportFormat.to_json())

# convert the object into a dict
jpg_export_format_dict = jpg_export_format_instance.to_dict()
# create an instance of JpgExportFormat from a dict
jpg_export_format_from_dict = JpgExportFormat.from_dict(jpg_export_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


