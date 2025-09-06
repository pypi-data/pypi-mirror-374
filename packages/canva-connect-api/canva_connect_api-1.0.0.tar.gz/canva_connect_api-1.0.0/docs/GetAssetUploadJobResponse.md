# GetAssetUploadJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**AssetUploadJob**](AssetUploadJob.md) |  | 

## Example

```python
from openapi_client.models.get_asset_upload_job_response import GetAssetUploadJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAssetUploadJobResponse from a JSON string
get_asset_upload_job_response_instance = GetAssetUploadJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetAssetUploadJobResponse.to_json())

# convert the object into a dict
get_asset_upload_job_response_dict = get_asset_upload_job_response_instance.to_dict()
# create an instance of GetAssetUploadJobResponse from a dict
get_asset_upload_job_response_from_dict = GetAssetUploadJobResponse.from_dict(get_asset_upload_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


