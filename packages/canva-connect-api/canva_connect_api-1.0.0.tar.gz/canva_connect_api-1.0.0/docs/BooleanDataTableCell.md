# BooleanDataTableCell

A boolean tabular data cell.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**value** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.boolean_data_table_cell import BooleanDataTableCell

# TODO update the JSON string below
json = "{}"
# create an instance of BooleanDataTableCell from a JSON string
boolean_data_table_cell_instance = BooleanDataTableCell.from_json(json)
# print the JSON string representation of the object
print(BooleanDataTableCell.to_json())

# convert the object into a dict
boolean_data_table_cell_dict = boolean_data_table_cell_instance.to_dict()
# create an instance of BooleanDataTableCell from a dict
boolean_data_table_cell_from_dict = BooleanDataTableCell.from_dict(boolean_data_table_cell_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


