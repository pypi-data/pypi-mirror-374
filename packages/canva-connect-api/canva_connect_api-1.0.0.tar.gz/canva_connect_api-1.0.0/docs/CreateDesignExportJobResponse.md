# CreateDesignExportJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**ExportJob**](ExportJob.md) |  | 

## Example

```python
from openapi_client.models.create_design_export_job_response import CreateDesignExportJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignExportJobResponse from a JSON string
create_design_export_job_response_instance = CreateDesignExportJobResponse.from_json(json)
# print the JSON string representation of the object
print(CreateDesignExportJobResponse.to_json())

# convert the object into a dict
create_design_export_job_response_dict = create_design_export_job_response_instance.to_dict()
# create an instance of CreateDesignExportJobResponse from a dict
create_design_export_job_response_from_dict = CreateDesignExportJobResponse.from_dict(create_design_export_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


