# NumberDataTableCell

A number tabular data cell.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**value** | **float** |  | [optional] 

## Example

```python
from openapi_client.models.number_data_table_cell import NumberDataTableCell

# TODO update the JSON string below
json = "{}"
# create an instance of NumberDataTableCell from a JSON string
number_data_table_cell_instance = NumberDataTableCell.from_json(json)
# print the JSON string representation of the object
print(NumberDataTableCell.to_json())

# convert the object into a dict
number_data_table_cell_dict = number_data_table_cell_instance.to_dict()
# create an instance of NumberDataTableCell from a dict
number_data_table_cell_from_dict = NumberDataTableCell.from_dict(number_data_table_cell_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


