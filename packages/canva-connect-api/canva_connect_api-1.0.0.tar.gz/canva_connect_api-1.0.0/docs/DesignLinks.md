# DesignLinks

A temporary set of URLs for viewing or editing the design.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**edit_url** | **str** | A temporary editing URL for the design. This URL is only accessible to the user that made the API request, and is designed to support [return navigation](https://www.canva.dev/docs/connect/return-navigation-guide/) workflows.  NOTE: This is not a permanent URL, it is only valid for 30 days. | 
**view_url** | **str** | A temporary viewing URL for the design. This URL is only accessible to the user that made the API request, and is designed to support [return navigation](https://www.canva.dev/docs/connect/return-navigation-guide/) workflows.  NOTE: This is not a permanent URL, it is only valid for 30 days.  | 

## Example

```python
from openapi_client.models.design_links import DesignLinks

# TODO update the JSON string below
json = "{}"
# create an instance of DesignLinks from a JSON string
design_links_instance = DesignLinks.from_json(json)
# print the JSON string representation of the object
print(DesignLinks.to_json())

# convert the object into a dict
design_links_dict = design_links_instance.to_dict()
# create an instance of DesignLinks from a dict
design_links_from_dict = DesignLinks.from_dict(design_links_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


