# DesignImportJobResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**designs** | [**List[DesignSummary]**](DesignSummary.md) | A list of designs imported from the external file. It usually contains one item. Imports with a large number of pages or assets are split into multiple designs. | 

## Example

```python
from openapi_client.models.design_import_job_result import DesignImportJobResult

# TODO update the JSON string below
json = "{}"
# create an instance of DesignImportJobResult from a JSON string
design_import_job_result_instance = DesignImportJobResult.from_json(json)
# print the JSON string representation of the object
print(DesignImportJobResult.to_json())

# convert the object into a dict
design_import_job_result_dict = design_import_job_result_instance.to_dict()
# create an instance of DesignImportJobResult from a dict
design_import_job_result_from_dict = DesignImportJobResult.from_dict(design_import_job_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


