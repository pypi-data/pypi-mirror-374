# DesignResizeJobResult

Design has been created and saved to user's root ([projects](https://www.canva.com/help/find-designs-and-folders/)) folder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**design** | [**DesignSummary**](DesignSummary.md) |  | 

## Example

```python
from openapi_client.models.design_resize_job_result import DesignResizeJobResult

# TODO update the JSON string below
json = "{}"
# create an instance of DesignResizeJobResult from a JSON string
design_resize_job_result_instance = DesignResizeJobResult.from_json(json)
# print the JSON string representation of the object
print(DesignResizeJobResult.to_json())

# convert the object into a dict
design_resize_job_result_dict = design_resize_job_result_instance.to_dict()
# create an instance of DesignResizeJobResult from a dict
design_resize_job_result_from_dict = DesignResizeJobResult.from_dict(design_resize_job_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


