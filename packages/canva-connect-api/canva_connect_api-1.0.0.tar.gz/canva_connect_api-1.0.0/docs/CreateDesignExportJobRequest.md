# CreateDesignExportJobRequest

Body parameters for starting an export job for a design. It must include a design ID, and one of the supported export formats.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**design_id** | **str** | The design ID. | 
**format** | [**ExportFormat**](ExportFormat.md) |  | 

## Example

```python
from openapi_client.models.create_design_export_job_request import CreateDesignExportJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignExportJobRequest from a JSON string
create_design_export_job_request_instance = CreateDesignExportJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateDesignExportJobRequest.to_json())

# convert the object into a dict
create_design_export_job_request_dict = create_design_export_job_request_instance.to_dict()
# create an instance of CreateDesignExportJobRequest from a dict
create_design_export_job_request_from_dict = CreateDesignExportJobRequest.from_dict(create_design_export_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


