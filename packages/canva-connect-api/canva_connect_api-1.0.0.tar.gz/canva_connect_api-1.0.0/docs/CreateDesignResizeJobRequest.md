# CreateDesignResizeJobRequest

Body parameters for starting a resize job for a design. It must include a design ID, and one of the supported design type.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**design_id** | **str** | The design ID. | 
**design_type** | [**DesignTypeInput**](DesignTypeInput.md) |  | 

## Example

```python
from openapi_client.models.create_design_resize_job_request import CreateDesignResizeJobRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDesignResizeJobRequest from a JSON string
create_design_resize_job_request_instance = CreateDesignResizeJobRequest.from_json(json)
# print the JSON string representation of the object
print(CreateDesignResizeJobRequest.to_json())

# convert the object into a dict
create_design_resize_job_request_dict = create_design_resize_job_request_instance.to_dict()
# create an instance of CreateDesignResizeJobRequest from a dict
create_design_resize_job_request_from_dict = CreateDesignResizeJobRequest.from_dict(create_design_resize_job_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


