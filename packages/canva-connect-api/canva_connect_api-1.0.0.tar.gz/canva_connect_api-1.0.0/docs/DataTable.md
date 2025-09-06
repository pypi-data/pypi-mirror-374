# DataTable

Tabular data, structured in rows of cells.  - The first row usually contains column headers. - Each cell must have a data type configured. - All rows must have the same number of cells. - Maximum of 100 rows and 20 columns.  WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rows** | [**List[DataTableRow]**](DataTableRow.md) | Rows of data.  The first row usually contains column headers. | 

## Example

```python
from openapi_client.models.data_table import DataTable

# TODO update the JSON string below
json = "{}"
# create an instance of DataTable from a JSON string
data_table_instance = DataTable.from_json(json)
# print the JSON string representation of the object
print(DataTable.to_json())

# convert the object into a dict
data_table_dict = data_table_instance.to_dict()
# create an instance of DataTable from a dict
data_table_from_dict = DataTable.from_dict(data_table_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


