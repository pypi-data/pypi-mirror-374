# ChartDataField

Chart data for a brand template. You can autofill the brand template with tabular data.  WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 

## Example

```python
from openapi_client.models.chart_data_field import ChartDataField

# TODO update the JSON string below
json = "{}"
# create an instance of ChartDataField from a JSON string
chart_data_field_instance = ChartDataField.from_json(json)
# print the JSON string representation of the object
print(ChartDataField.to_json())

# convert the object into a dict
chart_data_field_dict = chart_data_field_instance.to_dict()
# create an instance of ChartDataField from a dict
chart_data_field_from_dict = ChartDataField.from_dict(chart_data_field_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


