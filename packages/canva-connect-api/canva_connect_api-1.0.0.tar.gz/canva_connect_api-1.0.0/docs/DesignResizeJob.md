# DesignResizeJob

Details about the design resize job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The design resize job ID. | 
**status** | [**DesignResizeStatus**](DesignResizeStatus.md) |  | 
**result** | [**DesignResizeJobResult**](DesignResizeJobResult.md) |  | [optional] 
**error** | [**DesignResizeError**](DesignResizeError.md) |  | [optional] 

## Example

```python
from openapi_client.models.design_resize_job import DesignResizeJob

# TODO update the JSON string below
json = "{}"
# create an instance of DesignResizeJob from a JSON string
design_resize_job_instance = DesignResizeJob.from_json(json)
# print the JSON string representation of the object
print(DesignResizeJob.to_json())

# convert the object into a dict
design_resize_job_dict = design_resize_job_instance.to_dict()
# create an instance of DesignResizeJob from a dict
design_resize_job_from_dict = DesignResizeJob.from_dict(design_resize_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


