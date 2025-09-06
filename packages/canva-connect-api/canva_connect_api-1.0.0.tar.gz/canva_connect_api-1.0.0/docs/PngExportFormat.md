# PngExportFormat

Export the design as a PNG. Height or width (or both) may be specified, otherwise the file will be exported at it's default size. You may also specify whether to export the file losslessly, and whether to export a multi-page design as a single image.  If the user is on the Canva Free plan, the export height and width for a fixed-dimension design can't be upscaled by more than a factor of `1.125`.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**export_quality** | [**ExportQuality**](ExportQuality.md) |  | [optional] [default to ExportQuality.REGULAR]
**height** | **int** | Specify the height in pixels of the exported image. Note the following behavior:  - If no height or width is specified, the image is exported using the dimensions of the design. - If only one of height or width is specified, then the image is scaled to match that dimension, respecting the design&#39;s aspect ratio. - If both the height and width are specified, but the values don&#39;t match the design&#39;s aspect ratio, the export defaults to the larger dimension. | [optional] 
**width** | **int** | Specify the width in pixels of the exported image. Note the following behavior:  - If no width or height is specified, the image is exported using the dimensions of the design. - If only one of width or height is specified, then the image is scaled to match that dimension, respecting the design&#39;s aspect ratio. - If both the width and height are specified, but the values don&#39;t match the design&#39;s aspect ratio, the export defaults to the larger dimension. | [optional] 
**lossless** | **bool** | If set to &#x60;true&#x60; (default), the PNG is exported without compression. If set to &#x60;false&#x60;, the PNG is compressed using a lossy compression algorithm. Lossy PNG compression is only available to users on a Canva plan that has premium features, such as Canva Pro. If the user is on the Canva Free plan and this parameter is set to &#x60;false&#x60;, the export operation will fail. | [optional] [default to True]
**transparent_background** | **bool** | If set to &#x60;true&#x60;, the PNG is exported with a transparent background. This option is only available to users on a Canva plan that has premium features, such as Canva Pro. If the user is on the Canva Free plan and this parameter is set to &#x60;true&#x60;, the export operation will fail. | [optional] [default to False]
**as_single_image** | **bool** | When &#x60;true&#x60;, multi-page designs are merged into a single image. When &#x60;false&#x60; (default), each page is exported as a separate image. | [optional] [default to False]
**pages** | **List[int]** | To specify which pages to export in a multi-page design, provide the page numbers as an array. The first page in a design is page &#x60;1&#x60;. If &#x60;pages&#x60; isn&#39;t specified, all the pages are exported. | [optional] 

## Example

```python
from openapi_client.models.png_export_format import PngExportFormat

# TODO update the JSON string below
json = "{}"
# create an instance of PngExportFormat from a JSON string
png_export_format_instance = PngExportFormat.from_json(json)
# print the JSON string representation of the object
print(PngExportFormat.to_json())

# convert the object into a dict
png_export_format_dict = png_export_format_instance.to_dict()
# create an instance of PngExportFormat from a dict
png_export_format_from_dict = PngExportFormat.from_dict(png_export_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


