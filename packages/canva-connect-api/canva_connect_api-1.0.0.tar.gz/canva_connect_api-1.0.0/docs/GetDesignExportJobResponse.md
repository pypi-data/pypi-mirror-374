# GetDesignExportJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**ExportJob**](ExportJob.md) |  | 

## Example

```python
from openapi_client.models.get_design_export_job_response import GetDesignExportJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDesignExportJobResponse from a JSON string
get_design_export_job_response_instance = GetDesignExportJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetDesignExportJobResponse.to_json())

# convert the object into a dict
get_design_export_job_response_dict = get_design_export_job_response_instance.to_dict()
# create an instance of GetDesignExportJobResponse from a dict
get_design_export_job_response_from_dict = GetDesignExportJobResponse.from_dict(get_design_export_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


