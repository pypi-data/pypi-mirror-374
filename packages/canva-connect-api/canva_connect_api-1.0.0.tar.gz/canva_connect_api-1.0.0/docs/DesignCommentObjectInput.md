# DesignCommentObjectInput

If the comment is attached to a Canva Design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**design_id** | **str** | The ID of the design you want to attach this comment to. | 

## Example

```python
from openapi_client.models.design_comment_object_input import DesignCommentObjectInput

# TODO update the JSON string below
json = "{}"
# create an instance of DesignCommentObjectInput from a JSON string
design_comment_object_input_instance = DesignCommentObjectInput.from_json(json)
# print the JSON string representation of the object
print(DesignCommentObjectInput.to_json())

# convert the object into a dict
design_comment_object_input_dict = design_comment_object_input_instance.to_dict()
# create an instance of DesignCommentObjectInput from a dict
design_comment_object_input_from_dict = DesignCommentObjectInput.from_dict(design_comment_object_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


