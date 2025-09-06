# CreateDesignAutofillJobRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**brand_template_id** | **str** | ID of the input brand template. | 
**title** | **str** | Title to use for the autofilled design.  If no design title is provided, the autofilled design will have the same title as the brand template. | [optional] 
**data** | [**Dict[str, DatasetValue]**](DatasetValue.md) | Data object containing the data fields and values to autofill. | 

## Example

```python
from openapi_client.models.create_design_autofill_job_request import CreateDesignAutofillJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignAutofillJobRequest from a JSON string
create_design_autofill_job_request_instance = CreateDesignAutofillJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateDesignAutofillJobRequest.to_json())

# convert the object into a dict
create_design_autofill_job_request_dict = create_design_autofill_job_request_instance.to_dict()
# create an instance of CreateDesignAutofillJobRequest from a dict
create_design_autofill_job_request_from_dict = CreateDesignAutofillJobRequest.from_dict(create_design_autofill_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


