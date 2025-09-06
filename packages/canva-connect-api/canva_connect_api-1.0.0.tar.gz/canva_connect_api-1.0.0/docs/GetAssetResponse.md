# GetAssetResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**asset** | [**Asset**](Asset.md) |  | 

## Example

```python
from openapi_client.models.get_asset_response import GetAssetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAssetResponse from a JSON string
get_asset_response_instance = GetAssetResponse.from_json(json)
# print the JSON string representation of the object
print(GetAssetResponse.to_json())

# convert the object into a dict
get_asset_response_dict = get_asset_response_instance.to_dict()
# create an instance of GetAssetResponse from a dict
get_asset_response_from_dict = GetAssetResponse.from_dict(get_asset_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


