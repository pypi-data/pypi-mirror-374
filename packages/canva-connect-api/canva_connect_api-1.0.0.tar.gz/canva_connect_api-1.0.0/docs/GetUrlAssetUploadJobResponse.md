# GetUrlAssetUploadJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job** | [**AssetUploadJob**](AssetUploadJob.md) |  | 

## Example

```python
from openapi_client.models.get_url_asset_upload_job_response import GetUrlAssetUploadJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetUrlAssetUploadJobResponse from a JSON string
get_url_asset_upload_job_response_instance = GetUrlAssetUploadJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetUrlAssetUploadJobResponse.to_json())

# convert the object into a dict
get_url_asset_upload_job_response_dict = get_url_asset_upload_job_response_instance.to_dict()
# create an instance of GetUrlAssetUploadJobResponse from a dict
get_url_asset_upload_job_response_from_dict = GetUrlAssetUploadJobResponse.from_dict(get_url_asset_upload_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


