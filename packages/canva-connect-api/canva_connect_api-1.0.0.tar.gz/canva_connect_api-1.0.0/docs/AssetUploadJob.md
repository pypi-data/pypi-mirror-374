# AssetUploadJob

The status of the asset upload job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the asset upload job. | 
**status** | [**AssetUploadStatus**](AssetUploadStatus.md) |  | 
**error** | [**AssetUploadError**](AssetUploadError.md) |  | [optional] 
**asset** | [**Asset**](Asset.md) |  | [optional] 

## Example

```python
from openapi_client.models.asset_upload_job import AssetUploadJob

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadJob from a JSON string
asset_upload_job_instance = AssetUploadJob.from_json(json)
# print the JSON string representation of the object
print(AssetUploadJob.to_json())

# convert the object into a dict
asset_upload_job_dict = asset_upload_job_instance.to_dict()
# create an instance of AssetUploadJob from a dict
asset_upload_job_from_dict = AssetUploadJob.from_dict(asset_upload_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


