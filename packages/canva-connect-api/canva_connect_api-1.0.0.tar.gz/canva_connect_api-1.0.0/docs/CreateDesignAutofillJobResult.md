# CreateDesignAutofillJobResult

Design has been created and saved to user's root folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**design** | [**DesignSummary**](DesignSummary.md) |  | 

## Example

```python
from openapi_client.models.create_design_autofill_job_result import CreateDesignAutofillJobResult

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignAutofillJobResult from a JSON string
create_design_autofill_job_result_instance = CreateDesignAutofillJobResult.from_json(json)
# print the JSON string representation of the object
print(CreateDesignAutofillJobResult.to_json())

# convert the object into a dict
create_design_autofill_job_result_dict = create_design_autofill_job_result_instance.to_dict()
# create an instance of CreateDesignAutofillJobResult from a dict
create_design_autofill_job_result_from_dict = CreateDesignAutofillJobResult.from_dict(create_design_autofill_job_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


