# openapi_client.BrandTemplateApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_brand_template**](BrandTemplateApi.md#get_brand_template) | **GET** /v1/brand-templates/{brandTemplateId} | 
[**get_brand_template_dataset**](BrandTemplateApi.md#get_brand_template_dataset) | **GET** /v1/brand-templates/{brandTemplateId}/dataset | 
[**list_brand_templates**](BrandTemplateApi.md#list_brand_templates) | **GET** /v1/brand-templates | 


# **get_brand_template**
> GetBrandTemplateResponse get_brand_template(brand_template_id)

<Warning>

Soon, all brand template IDs will be updated to a new format. If your integration stores brand template IDs, you'll need to migrate to use the new IDs. After we implement this change, you'll have 6 months to migrate before the old IDs are removed.

</Warning>

<Note>

To use this API, your integration must act on behalf of a user that's a member of a [Canva Enterprise](https://www.canva.com/enterprise/) organization.

</Note>

Retrieves the metadata for a brand template.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_brand_template_response import GetBrandTemplateResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BrandTemplateApi(api_client)
    brand_template_id = 'brand_template_id_example' # str | The brand template ID.

    try:
        api_response = api_instance.get_brand_template(brand_template_id)
        print("The response of BrandTemplateApi->get_brand_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandTemplateApi->get_brand_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **brand_template_id** | **str**| The brand template ID. | 

### Return type

[**GetBrandTemplateResponse**](GetBrandTemplateResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_brand_template_dataset**
> GetBrandTemplateDatasetResponse get_brand_template_dataset(brand_template_id)

<Warning>

Soon, all brand template IDs will be updated to a new format. If your integration stores brand template IDs, you'll need to migrate to use the new IDs. After we implement this change, you'll have 6 months to migrate before the old IDs are removed.

</Warning>

<Note>

To use this API, your integration must act on behalf of a user that's a member of a [Canva Enterprise](https://www.canva.com/enterprise/) organization.

</Note>

Gets the dataset definition of a brand template. If the brand
template contains autofill data fields, this API returns an object with the data field
names and the type of data they accept.

Available data field types include:

- Images
- Text
- Charts

You can autofill a brand template using the [Create a design autofill job
API](https://www.canva.dev/docs/connect/api-reference/autofills/create-design-autofill-job/).

WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_brand_template_dataset_response import GetBrandTemplateDatasetResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BrandTemplateApi(api_client)
    brand_template_id = 'brand_template_id_example' # str | The brand template ID.

    try:
        api_response = api_instance.get_brand_template_dataset(brand_template_id)
        print("The response of BrandTemplateApi->get_brand_template_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandTemplateApi->get_brand_template_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **brand_template_id** | **str**| The brand template ID. | 

### Return type

[**GetBrandTemplateDatasetResponse**](GetBrandTemplateDatasetResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_brand_templates**
> ListBrandTemplatesResponse list_brand_templates(query=query, continuation=continuation, ownership=ownership, sort_by=sort_by, dataset=dataset)

<Warning>

Soon, all brand template IDs will be updated to a new format. If your integration stores brand template IDs, you'll need to migrate to use the new IDs. After we implement this change, you'll have 6 months to migrate before the old IDs are removed.

</Warning>

<Note>

To use this API, your integration must act on behalf of a user that's a member of a [Canva Enterprise](https://www.canva.com/enterprise/) organization.

</Note>

Get a list of the [brand templates](https://www.canva.com/help/publish-team-template/) the user has access to.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.dataset_filter import DatasetFilter
from openapi_client.models.list_brand_templates_response import ListBrandTemplatesResponse
from openapi_client.models.ownership_type import OwnershipType
from openapi_client.models.sort_by_type import SortByType
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.canva.com/rest
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.canva.com/rest"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.BrandTemplateApi(api_client)
    query = 'query_example' # str | Lets you search the brand templates available to the user using a search term or terms. (optional)
    continuation = 'continuation_example' # str | If the success response contains a continuation token, the user has access to more brand templates you can list. You can use this token as a query parameter and retrieve more templates from the list, for example `/v1/brand-templates?continuation={continuation}`. To retrieve all the brand templates available to the user, you might need to make multiple requests. (optional)
    ownership = any # OwnershipType | Filter the list of brand templates based on the user's ownership of the brand templates. (optional) (default to any)
    sort_by = relevance # SortByType | Sort the list of brand templates. (optional) (default to relevance)
    dataset = any # DatasetFilter | Filter the list of brand templates based on the brand templates' dataset definitions. Brand templates with dataset definitions are mainly used with the [Autofill APIs](https://www.canva.dev/docs/connect/api-reference/autofills/). (optional) (default to any)

    try:
        api_response = api_instance.list_brand_templates(query=query, continuation=continuation, ownership=ownership, sort_by=sort_by, dataset=dataset)
        print("The response of BrandTemplateApi->list_brand_templates:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandTemplateApi->list_brand_templates: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| Lets you search the brand templates available to the user using a search term or terms. | [optional] 
 **continuation** | **str**| If the success response contains a continuation token, the user has access to more brand templates you can list. You can use this token as a query parameter and retrieve more templates from the list, for example &#x60;/v1/brand-templates?continuation&#x3D;{continuation}&#x60;. To retrieve all the brand templates available to the user, you might need to make multiple requests. | [optional] 
 **ownership** | [**OwnershipType**](.md)| Filter the list of brand templates based on the user&#39;s ownership of the brand templates. | [optional] [default to any]
 **sort_by** | [**SortByType**](.md)| Sort the list of brand templates. | [optional] [default to relevance]
 **dataset** | [**DatasetFilter**](.md)| Filter the list of brand templates based on the brand templates&#39; dataset definitions. Brand templates with dataset definitions are mainly used with the [Autofill APIs](https://www.canva.dev/docs/connect/api-reference/autofills/). | [optional] [default to any]

### Return type

[**ListBrandTemplatesResponse**](ListBrandTemplatesResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

