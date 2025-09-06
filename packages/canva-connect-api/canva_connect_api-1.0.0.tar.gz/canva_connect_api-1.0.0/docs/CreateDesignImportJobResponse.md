# CreateDesignImportJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**DesignImportJob**](DesignImportJob.md) |  | 

## Example

```python
from openapi_client.models.create_design_import_job_response import CreateDesignImportJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignImportJobResponse from a JSON string
create_design_import_job_response_instance = CreateDesignImportJobResponse.from_json(json)
# print the JSON string representation of the object
print(CreateDesignImportJobResponse.to_json())

# convert the object into a dict
create_design_import_job_response_dict = create_design_import_job_response_instance.to_dict()
# create an instance of CreateDesignImportJobResponse from a dict
create_design_import_job_response_from_dict = CreateDesignImportJobResponse.from_dict(create_design_import_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


