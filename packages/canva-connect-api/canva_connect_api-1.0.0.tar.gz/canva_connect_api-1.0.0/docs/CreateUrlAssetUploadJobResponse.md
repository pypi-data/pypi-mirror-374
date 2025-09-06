# CreateUrlAssetUploadJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**AssetUploadJob**](AssetUploadJob.md) |  | 

## Example

```python
from openapi_client.models.create_url_asset_upload_job_response import CreateUrlAssetUploadJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUrlAssetUploadJobResponse from a JSON string
create_url_asset_upload_job_response_instance = CreateUrlAssetUploadJobResponse.from_json(json)
# print the JSON string representation of the object
print(CreateUrlAssetUploadJobResponse.to_json())

# convert the object into a dict
create_url_asset_upload_job_response_dict = create_url_asset_upload_job_response_instance.to_dict()
# create an instance of CreateUrlAssetUploadJobResponse from a dict
create_url_asset_upload_job_response_from_dict = CreateUrlAssetUploadJobResponse.from_dict(create_url_asset_upload_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


