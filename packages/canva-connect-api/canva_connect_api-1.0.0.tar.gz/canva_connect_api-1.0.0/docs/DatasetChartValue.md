# DatasetChartValue

If the data field is a chart.   WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**chart_data** | [**DataTable**](DataTable.md) |  | 

## Example

```python
from openapi_client.models.dataset_chart_value import DatasetChartValue

# TODO update the JSON string below
json = "{}"
# create an instance of DatasetChartValue from a JSON string
dataset_chart_value_instance = DatasetChartValue.from_json(json)
# print the JSON string representation of the object
print(DatasetChartValue.to_json())

# convert the object into a dict
dataset_chart_value_dict = dataset_chart_value_instance.to_dict()
# create an instance of DatasetChartValue from a dict
dataset_chart_value_from_dict = DatasetChartValue.from_dict(dataset_chart_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


