# DesignCommentObject

If the comment is attached to a Canva Design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**design_id** | **str** | The ID of the design this comment is attached to. | 

## Example

```python
from openapi_client.models.design_comment_object import DesignCommentObject

# TODO update the JSON string below
json = "{}"
# create an instance of DesignCommentObject from a JSON string
design_comment_object_instance = DesignCommentObject.from_json(json)
# print the JSON string representation of the object
print(DesignCommentObject.to_json())

# convert the object into a dict
design_comment_object_dict = design_comment_object_instance.to_dict()
# create an instance of DesignCommentObject from a dict
design_comment_object_from_dict = DesignCommentObject.from_dict(design_comment_object_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


