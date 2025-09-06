# CreateUrlImportJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | A title for the design. | 
**url** | **str** | The URL of the file to import. This URL must be accessible from the internet and be publicly available. | 
**mime_type** | **str** | The MIME type of the file being imported. If not provided, Canva attempts to automatically detect the type of the file. | [optional] 

## Example

```python
from openapi_client.models.create_url_import_job_request import CreateUrlImportJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUrlImportJobRequest from a JSON string
create_url_import_job_request_instance = CreateUrlImportJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateUrlImportJobRequest.to_json())

# convert the object into a dict
create_url_import_job_request_dict = create_url_import_job_request_instance.to_dict()
# create an instance of CreateUrlImportJobRequest from a dict
create_url_import_job_request_from_dict = CreateUrlImportJobRequest.from_dict(create_url_import_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


