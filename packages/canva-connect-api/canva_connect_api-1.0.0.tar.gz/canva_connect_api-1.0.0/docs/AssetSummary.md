# AssetSummary

An object representing an asset with associated metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**AssetType**](AssetType.md) |  | 
**id** | **str** | The ID of the asset. | 
**name** | **str** | The name of the asset. | 
**tags** | **List[str]** | The user-facing tags attached to the asset. Users can add these tags to their uploaded assets, and they can search their uploaded assets in the Canva UI by searching for these tags. For information on how users use tags, see the [Canva Help Center page on asset tags](https://www.canva.com/help/add-edit-tags/). | 
**created_at** | **int** | When the asset was added to Canva, as a Unix timestamp (in seconds since the Unix Epoch). | 
**updated_at** | **int** | When the asset was last updated in Canva, as a Unix timestamp (in seconds since the Unix Epoch). | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | [optional] 

## Example

```python
from openapi_client.models.asset_summary import AssetSummary

# TODO update the JSON string below
json = "{}"
# create an instance of AssetSummary from a JSON string
asset_summary_instance = AssetSummary.from_json(json)
# print the JSON string representation of the object
print(AssetSummary.to_json())

# convert the object into a dict
asset_summary_dict = asset_summary_instance.to_dict()
# create an instance of AssetSummary from a dict
asset_summary_from_dict = AssetSummary.from_dict(asset_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


