# UpdateAssetResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**asset** | [**Asset**](Asset.md) |  | 

## Example

```python
from openapi_client.models.update_asset_response import UpdateAssetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateAssetResponse from a JSON string
update_asset_response_instance = UpdateAssetResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateAssetResponse.to_json())

# convert the object into a dict
update_asset_response_dict = update_asset_response_instance.to_dict()
# create an instance of UpdateAssetResponse from a dict
update_asset_response_from_dict = UpdateAssetResponse.from_dict(update_asset_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


