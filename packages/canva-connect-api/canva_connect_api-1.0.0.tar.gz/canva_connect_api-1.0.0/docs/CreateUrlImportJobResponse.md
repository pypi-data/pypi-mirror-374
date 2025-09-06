# CreateUrlImportJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**DesignImportJob**](DesignImportJob.md) |  | 

## Example

```python
from openapi_client.models.create_url_import_job_response import CreateUrlImportJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUrlImportJobResponse from a JSON string
create_url_import_job_response_instance = CreateUrlImportJobResponse.from_json(json)
# print the JSON string representation of the object
print(CreateUrlImportJobResponse.to_json())

# convert the object into a dict
create_url_import_job_response_dict = create_url_import_job_response_instance.to_dict()
# create an instance of CreateUrlImportJobResponse from a dict
create_url_import_job_response_from_dict = CreateUrlImportJobResponse.from_dict(create_url_import_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


