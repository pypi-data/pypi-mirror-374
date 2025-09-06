# Asset

The asset object, which contains metadata about the asset.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**AssetType**](AssetType.md) |  | 
**id** | **str** | The ID of the asset. | 
**name** | **str** | The name of the asset. | 
**tags** | **List[str]** | The user-facing tags attached to the asset. Users can add these tags to their uploaded assets, and they can search their uploaded assets in the Canva UI by searching for these tags. For information on how users use tags, see the [Canva Help Center page on asset tags](https://www.canva.com/help/add-edit-tags/). | 
**import_status** | [**ImportStatus**](ImportStatus.md) |  | [optional] 
**created_at** | **int** | When the asset was added to Canva, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the asset was last updated in Canva, as a Unix timestamp (in seconds since the Unix Epoch). | 
**owner** | [**TeamUserSummary**](TeamUserSummary.md) |  | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | [optional] 

## Example

```python
from openapi_client.models.asset import Asset

# TODO update the JSON string below
json = "{}"
# create an instance of Asset from a JSON string
asset_instance = Asset.from_json(json)
# print the JSON string representation of the object
print(Asset.to_json())

# convert the object into a dict
asset_dict = asset_instance.to_dict()
# create an instance of Asset from a dict
asset_from_dict = Asset.from_dict(asset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


