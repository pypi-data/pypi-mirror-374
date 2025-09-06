# ExportJob

The status of the export job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The export job ID. | 
**status** | [**DesignExportStatus**](DesignExportStatus.md) |  | 
**urls** | **List[str]** | Download URL(s) for the completed export job. These URLs expire after 24 hours.  Depending on the design type and export format, there is a download URL for each page in the design. The list is sorted by page order. | [optional] 
**error** | [**ExportError**](ExportError.md) |  | [optional] 

## Example

```python
from openapi_client.models.export_job import ExportJob

# TODO update the JSON string below
json = "{}"
# create an instance of ExportJob from a JSON string
export_job_instance = ExportJob.from_json(json)
# print the JSON string representation of the object
print(ExportJob.to_json())

# convert the object into a dict
export_job_dict = export_job_instance.to_dict()
# create an instance of ExportJob from a dict
export_job_from_dict = ExportJob.from_dict(export_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


