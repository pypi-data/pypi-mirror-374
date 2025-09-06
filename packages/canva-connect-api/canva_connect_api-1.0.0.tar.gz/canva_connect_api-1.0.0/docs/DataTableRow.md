# DataTableRow

A single row of tabular data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cells** | [**List[DataTableCell]**](DataTableCell.md) | Cells of data in row.  All rows must have the same number of cells. | 

## Example

```python
from openapi_client.models.data_table_row import DataTableRow

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableRow from a JSON string
data_table_row_instance = DataTableRow.from_json(json)
# print the JSON string representation of the object
print(DataTableRow.to_json())

# convert the object into a dict
data_table_row_dict = data_table_row_instance.to_dict()
# create an instance of DataTableRow from a dict
data_table_row_from_dict = DataTableRow.from_dict(data_table_row_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


