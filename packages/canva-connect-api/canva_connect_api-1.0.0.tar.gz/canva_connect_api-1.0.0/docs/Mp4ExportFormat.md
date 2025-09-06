# Mp4ExportFormat

Export the design as an MP4. You must specify the quality of the exported video.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**export_quality** | [**ExportQuality**](ExportQuality.md) |  | [optional] [default to ExportQuality.REGULAR]
**quality** | [**Mp4ExportQuality**](Mp4ExportQuality.md) |  | 
**pages** | **List[int]** | To specify which pages to export in a multi-page design, provide the page numbers as an array. The first page in a design is page &#x60;1&#x60;. If &#x60;pages&#x60; isn&#39;t specified, all the pages are exported. | [optional] 

## Example

```python
from openapi_client.models.mp4_export_format import Mp4ExportFormat

# TODO update the JSON string below
json = "{}"
# create an instance of Mp4ExportFormat from a JSON string
mp4_export_format_instance = Mp4ExportFormat.from_json(json)
# print the JSON string representation of the object
print(Mp4ExportFormat.to_json())

# convert the object into a dict
mp4_export_format_dict = mp4_export_format_instance.to_dict()
# create an instance of Mp4ExportFormat from a dict
mp4_export_format_from_dict = Mp4ExportFormat.from_dict(mp4_export_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


