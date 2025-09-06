# CreateUrlAssetUploadJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A name for the asset. | 
**url** | **str** | The URL of the file to import. This URL must be accessible from the internet and be publicly available. | 

## Example

```python
from openapi_client.models.create_url_asset_upload_job_request import CreateUrlAssetUploadJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUrlAssetUploadJobRequest from a JSON string
create_url_asset_upload_job_request_instance = CreateUrlAssetUploadJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateUrlAssetUploadJobRequest.to_json())

# convert the object into a dict
create_url_asset_upload_job_request_dict = create_url_asset_upload_job_request_instance.to_dict()
# create an instance of CreateUrlAssetUploadJobRequest from a dict
create_url_asset_upload_job_request_from_dict = CreateUrlAssetUploadJobRequest.from_dict(create_url_asset_upload_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


