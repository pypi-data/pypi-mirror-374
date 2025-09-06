# DataTableCell

A single tabular data cell.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**value** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.data_table_cell import DataTableCell

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableCell from a JSON string
data_table_cell_instance = DataTableCell.from_json(json)
# print the JSON string representation of the object
print(DataTableCell.to_json())

# convert the object into a dict
data_table_cell_dict = data_table_cell_instance.to_dict()
# create an instance of DataTableCell from a dict
data_table_cell_from_dict = DataTableCell.from_dict(data_table_cell_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


