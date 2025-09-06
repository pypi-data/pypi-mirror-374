# DesignImportJob

The status of the design import job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the design import job. | 
**status** | [**DesignImportStatus**](DesignImportStatus.md) |  | 
**result** | [**DesignImportJobResult**](DesignImportJobResult.md) |  | [optional] 
**error** | [**DesignImportError**](DesignImportError.md) |  | [optional] 

## Example

```python
from openapi_client.models.design_import_job import DesignImportJob

# TODO update the JSON string below
json = "{}"
# create an instance of DesignImportJob from a JSON string
design_import_job_instance = DesignImportJob.from_json(json)
# print the JSON string representation of the object
print(DesignImportJob.to_json())

# convert the object into a dict
design_import_job_dict = design_import_job_instance.to_dict()
# create an instance of DesignImportJob from a dict
design_import_job_from_dict = DesignImportJob.from_dict(design_import_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


