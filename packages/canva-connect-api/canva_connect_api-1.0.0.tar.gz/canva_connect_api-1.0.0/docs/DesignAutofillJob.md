# DesignAutofillJob

Details about the autofill job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | ID of the asynchronous job that is creating the design using the provided data. | 
**status** | [**DesignAutofillStatus**](DesignAutofillStatus.md) |  | 
**result** | [**CreateDesignAutofillJobResult**](CreateDesignAutofillJobResult.md) |  | [optional] 
**error** | [**AutofillError**](AutofillError.md) |  | [optional] 

## Example

```python
from openapi_client.models.design_autofill_job import DesignAutofillJob

# TODO update the JSON string below
json = "{}"
# create an instance of DesignAutofillJob from a JSON string
design_autofill_job_instance = DesignAutofillJob.from_json(json)
# print the JSON string representation of the object
print(DesignAutofillJob.to_json())

# convert the object into a dict
design_autofill_job_dict = design_autofill_job_instance.to_dict()
# create an instance of DesignAutofillJob from a dict
design_autofill_job_from_dict = DesignAutofillJob.from_dict(design_autofill_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


