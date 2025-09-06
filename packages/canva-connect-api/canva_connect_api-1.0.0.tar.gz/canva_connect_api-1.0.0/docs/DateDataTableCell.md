# DateDataTableCell

A date tabular data cell.  Specified as a Unix timestamp (in seconds since the Unix Epoch).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**value** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.date_data_table_cell import DateDataTableCell

# TODO update the JSON string below
json = "{}"
# create an instance of DateDataTableCell from a JSON string
date_data_table_cell_instance = DateDataTableCell.from_json(json)
# print the JSON string representation of the object
print(DateDataTableCell.to_json())

# convert the object into a dict
date_data_table_cell_dict = date_data_table_cell_instance.to_dict()
# create an instance of DateDataTableCell from a dict
date_data_table_cell_from_dict = DateDataTableCell.from_dict(date_data_table_cell_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


