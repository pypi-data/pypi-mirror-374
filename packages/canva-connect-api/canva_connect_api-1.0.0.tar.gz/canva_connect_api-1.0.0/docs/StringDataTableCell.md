# StringDataTableCell

A string tabular data cell.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**value** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.string_data_table_cell import StringDataTableCell

# TODO update the JSON string below
json = "{}"
# create an instance of StringDataTableCell from a JSON string
string_data_table_cell_instance = StringDataTableCell.from_json(json)
# print the JSON string representation of the object
print(StringDataTableCell.to_json())

# convert the object into a dict
string_data_table_cell_dict = string_data_table_cell_instance.to_dict()
# create an instance of StringDataTableCell from a dict
string_data_table_cell_from_dict = StringDataTableCell.from_dict(string_data_table_cell_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


