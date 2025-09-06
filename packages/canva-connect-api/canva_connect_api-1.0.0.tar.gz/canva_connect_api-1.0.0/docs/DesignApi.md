# openapi_client.DesignApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_design**](DesignApi.md#create_design) | **POST** /v1/designs | 
[**get_design**](DesignApi.md#get_design) | **GET** /v1/designs/{designId} | 
[**get_design_export_formats**](DesignApi.md#get_design_export_formats) | **GET** /v1/designs/{designId}/export-formats | 
[**get_design_pages**](DesignApi.md#get_design_pages) | **GET** /v1/designs/{designId}/pages | 
[**list_designs**](DesignApi.md#list_designs) | **GET** /v1/designs | 


# **create_design**
> CreateDesignResponse create_design(create_design_request=create_design_request)

Creates a new Canva design. To create a new design, you can either:

- Use a preset design type.
- Set height and width dimensions for a custom design.

Additionally, you can also provide the `asset_id` of an asset in the user's [projects](https://www.canva.com/help/find-designs-and-folders/) to add to the new design. Currently, this only supports image assets. To list the assets in a folder in the user's projects, use the [List folder items API](https://www.canva.dev/docs/connect/api-reference/folders/list-folder-items/).

NOTE: Blank designs created with this API are automatically deleted if they're not edited within 7 days. These blank designs bypass the user's Canva trash and are permanently deleted.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_design_request import CreateDesignRequest
from openapi_client.models.create_design_response import CreateDesignResponse
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
    api_instance = openapi_client.DesignApi(api_client)
    create_design_request = openapi_client.CreateDesignRequest() # CreateDesignRequest |  (optional)

    try:
        api_response = api_instance.create_design(create_design_request=create_design_request)
        print("The response of DesignApi->create_design:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignApi->create_design: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_design_request** | [**CreateDesignRequest**](CreateDesignRequest.md)|  | [optional] 

### Return type

[**CreateDesignResponse**](CreateDesignResponse.md)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_design**
> GetDesignResponse get_design(design_id)

Gets the metadata for a design. This includes owner information, URLs for editing and viewing, and thumbnail information.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_response import GetDesignResponse
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
    api_instance = openapi_client.DesignApi(api_client)
    design_id = 'design_id_example' # str | The design ID.

    try:
        api_response = api_instance.get_design(design_id)
        print("The response of DesignApi->get_design:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignApi->get_design: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 

### Return type

[**GetDesignResponse**](GetDesignResponse.md)

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

# **get_design_export_formats**
> GetDesignExportFormatsResponse get_design_export_formats(design_id)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Lists the available file formats for [exporting a design](https://www.canva.dev/docs/connect/api-reference/exports/create-design-export-job/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_export_formats_response import GetDesignExportFormatsResponse
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
    api_instance = openapi_client.DesignApi(api_client)
    design_id = 'design_id_example' # str | The design ID.

    try:
        api_response = api_instance.get_design_export_formats(design_id)
        print("The response of DesignApi->get_design_export_formats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignApi->get_design_export_formats: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 

### Return type

[**GetDesignExportFormatsResponse**](GetDesignExportFormatsResponse.md)

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

# **get_design_pages**
> GetDesignPagesResponse get_design_pages(design_id, offset=offset, limit=limit)

<Warning>

This API is currently provided as a preview. Be aware of the following:

- There might be unannounced breaking changes.
- Any breaking changes to preview APIs won't produce a new [API version](https://www.canva.dev/docs/connect/versions/).
- Public integrations that use preview APIs will not pass the review process, and can't be made available to all Canva users.

</Warning>

Lists metadata for pages in a design, such as page-specific thumbnails.

For the specified design, you can provide `offset` and `limit` values to specify the range of pages to return.

NOTE: Some design types don't have pages (for example, Canva docs).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_design_pages_response import GetDesignPagesResponse
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
    api_instance = openapi_client.DesignApi(api_client)
    design_id = 'design_id_example' # str | The design ID.
    offset = 1 # int | The page index to start the range of pages to return.  Pages are indexed using one-based numbering, so the first page in a design has the index value `1`.  (optional) (default to 1)
    limit = 50 # int | The number of pages to return, starting at the page index specified using the `offset` parameter. (optional) (default to 50)

    try:
        api_response = api_instance.get_design_pages(design_id, offset=offset, limit=limit)
        print("The response of DesignApi->get_design_pages:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignApi->get_design_pages: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **design_id** | **str**| The design ID. | 
 **offset** | **int**| The page index to start the range of pages to return.  Pages are indexed using one-based numbering, so the first page in a design has the index value &#x60;1&#x60;.  | [optional] [default to 1]
 **limit** | **int**| The number of pages to return, starting at the page index specified using the &#x60;offset&#x60; parameter. | [optional] [default to 50]

### Return type

[**GetDesignPagesResponse**](GetDesignPagesResponse.md)

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

# **list_designs**
> GetListDesignResponse list_designs(query=query, continuation=continuation, ownership=ownership, sort_by=sort_by)

Lists metadata for all the designs in a Canva user's
[projects](https://www.canva.com/help/find-designs-and-folders/). You can also:

- Use search terms to filter the listed designs.
- Show designs either created by, or shared with the user.
- Sort the results.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_list_design_response import GetListDesignResponse
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
    api_instance = openapi_client.DesignApi(api_client)
    query = 'party invites' # str | Lets you search the user's designs, and designs shared with the user, using a search term or terms. (optional)
    continuation = 'RkFGMgXlsVTDbMd:MR3L0QjiaUzycIAjx0yMyuNiV0OildoiOwL0x32G4NjNu4FwtAQNxowUQNMMYN' # str | If the success response contains a continuation token, the list contains more designs you can list. You can use this token as a query parameter and retrieve more designs from the list, for example `/v1/designs?continuation={continuation}`.  To retrieve all of a user's designs, you might need to make multiple requests. (optional)
    ownership = any # OwnershipType | Filter the list of designs based on the user's ownership of the designs. (optional) (default to any)
    sort_by = relevance # SortByType | Sort the list of designs. (optional) (default to relevance)

    try:
        api_response = api_instance.list_designs(query=query, continuation=continuation, ownership=ownership, sort_by=sort_by)
        print("The response of DesignApi->list_designs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DesignApi->list_designs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| Lets you search the user&#39;s designs, and designs shared with the user, using a search term or terms. | [optional] 
 **continuation** | **str**| If the success response contains a continuation token, the list contains more designs you can list. You can use this token as a query parameter and retrieve more designs from the list, for example &#x60;/v1/designs?continuation&#x3D;{continuation}&#x60;.  To retrieve all of a user&#39;s designs, you might need to make multiple requests. | [optional] 
 **ownership** | [**OwnershipType**](.md)| Filter the list of designs based on the user&#39;s ownership of the designs. | [optional] [default to any]
 **sort_by** | [**SortByType**](.md)| Sort the list of designs. | [optional] [default to relevance]

### Return type

[**GetListDesignResponse**](GetListDesignResponse.md)

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

