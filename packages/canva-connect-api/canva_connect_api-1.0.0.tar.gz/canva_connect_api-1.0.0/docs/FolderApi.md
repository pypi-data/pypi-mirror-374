# openapi_client.FolderApi

All URIs are relative to *https://api.canva.com/rest*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_folder**](FolderApi.md#create_folder) | **POST** /v1/folders | 
[**delete_folder**](FolderApi.md#delete_folder) | **DELETE** /v1/folders/{folderId} | 
[**get_folder**](FolderApi.md#get_folder) | **GET** /v1/folders/{folderId} | 
[**list_folder_items**](FolderApi.md#list_folder_items) | **GET** /v1/folders/{folderId}/items | 
[**move_folder_item**](FolderApi.md#move_folder_item) | **POST** /v1/folders/move | 
[**update_folder**](FolderApi.md#update_folder) | **PATCH** /v1/folders/{folderId} | 


# **create_folder**
> CreateFolderResponse create_folder(create_folder_request)

Creates a folder in one of the following locations:

- The top level of a Canva user's [projects](https://www.canva.com/help/find-designs-and-folders/) (using the ID `root`),
- The user's Uploads folder (using the ID `uploads`),
- Another folder (using the parent folder's ID).

When a folder is successfully created, the
endpoint returns its folder ID, along with other information.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.create_folder_request import CreateFolderRequest
from openapi_client.models.create_folder_response import CreateFolderResponse
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
    api_instance = openapi_client.FolderApi(api_client)
    create_folder_request = openapi_client.CreateFolderRequest() # CreateFolderRequest | 

    try:
        api_response = api_instance.create_folder(create_folder_request)
        print("The response of FolderApi->create_folder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FolderApi->create_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_folder_request** | [**CreateFolderRequest**](CreateFolderRequest.md)|  | 

### Return type

[**CreateFolderResponse**](CreateFolderResponse.md)

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

# **delete_folder**
> delete_folder(folder_id)

Deletes a folder with the specified `folderID`.
Deleting a folder moves the user's content in the folder to the
[Trash](https://www.canva.com/help/deleted-designs/) and content owned by
other users is moved to the top level of the owner's
[projects](https://www.canva.com/help/find-designs-and-folders/).

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
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
    api_instance = openapi_client.FolderApi(api_client)
    folder_id = 'FAF2lZtloor' # str | The folder ID.

    try:
        api_instance.delete_folder(folder_id)
    except Exception as e:
        print("Exception when calling FolderApi->delete_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The folder ID. | 

### Return type

void (empty response body)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_folder**
> GetFolderResponse get_folder(folder_id)

Gets the name and other details of a folder using a folder's `folderID`.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.get_folder_response import GetFolderResponse
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
    api_instance = openapi_client.FolderApi(api_client)
    folder_id = 'FAF2lZtloor' # str | The folder ID.

    try:
        api_response = api_instance.get_folder(folder_id)
        print("The response of FolderApi->get_folder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FolderApi->get_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The folder ID. | 

### Return type

[**GetFolderResponse**](GetFolderResponse.md)

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

# **list_folder_items**
> ListFolderItemsResponse list_folder_items(folder_id, continuation=continuation, item_types=item_types, sort_by=sort_by)

Lists the items in a folder, including each item's `type`.

Folders can contain:

- Other folders.
- Designs, such as Instagram posts, Presentations, and Documents ([Canva Docs](https://www.canva.com/create/documents/)).
- Image assets.

Currently, video assets are not returned in the response.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.folder_item_sort_by import FolderItemSortBy
from openapi_client.models.folder_item_type import FolderItemType
from openapi_client.models.list_folder_items_response import ListFolderItemsResponse
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
    api_instance = openapi_client.FolderApi(api_client)
    folder_id = 'FAF2lZtloor' # str | The folder ID.
    continuation = 'RkFGMgXlsVTDbMd:MR3L0QjiaUzycIAjx0yMyuNiV0OildoiOwL0x32G4NjNu4FwtAQNxowUQNMMYN' # str | If the success response contains a continuation token, the folder contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example `/v1/folders/{folderId}/items?continuation={continuation}`.  To retrieve all the items in a folder, you might need to make multiple requests. (optional)
    item_types = [openapi_client.FolderItemType()] # List[FolderItemType] | Filter the folder items to only return specified types. The available types are: `design`, `folder`, and `image`. To filter for more than one item type, provide a comma- delimited list. (optional)
    sort_by = modified_descending # FolderItemSortBy | Sort the list of folder items. (optional) (default to modified_descending)

    try:
        api_response = api_instance.list_folder_items(folder_id, continuation=continuation, item_types=item_types, sort_by=sort_by)
        print("The response of FolderApi->list_folder_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FolderApi->list_folder_items: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The folder ID. | 
 **continuation** | **str**| If the success response contains a continuation token, the folder contains more items you can list. You can use this token as a query parameter and retrieve more items from the list, for example &#x60;/v1/folders/{folderId}/items?continuation&#x3D;{continuation}&#x60;.  To retrieve all the items in a folder, you might need to make multiple requests. | [optional] 
 **item_types** | [**List[FolderItemType]**](FolderItemType.md)| Filter the folder items to only return specified types. The available types are: &#x60;design&#x60;, &#x60;folder&#x60;, and &#x60;image&#x60;. To filter for more than one item type, provide a comma- delimited list. | [optional] 
 **sort_by** | [**FolderItemSortBy**](.md)| Sort the list of folder items. | [optional] [default to modified_descending]

### Return type

[**ListFolderItemsResponse**](ListFolderItemsResponse.md)

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

# **move_folder_item**
> move_folder_item(move_folder_item_request=move_folder_item_request)

Moves an item to another folder. You must specify the folder ID of the destination folder, as well as the ID of the item you want to move.

NOTE: In some situations, a single item can exist in multiple folders. If you attempt to move an item that exists in multiple folders, the API returns an `item_in_multiple_folders` error. In this case, you must use the Canva UI to move the item to another folder.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.move_folder_item_request import MoveFolderItemRequest
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
    api_instance = openapi_client.FolderApi(api_client)
    move_folder_item_request = openapi_client.MoveFolderItemRequest() # MoveFolderItemRequest |  (optional)

    try:
        api_instance.move_folder_item(move_folder_item_request=move_folder_item_request)
    except Exception as e:
        print("Exception when calling FolderApi->move_folder_item: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **move_folder_item_request** | [**MoveFolderItemRequest**](MoveFolderItemRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[oauthAuthCode](../README.md#oauthAuthCode)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | OK |  -  |
**0** | Error Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_folder**
> UpdateFolderResponse update_folder(folder_id, update_folder_request)

Updates a folder's details using its `folderID`.
Currently, you can only update a folder's name.

### Example

* OAuth Authentication (oauthAuthCode):

```python
import openapi_client
from openapi_client.models.update_folder_request import UpdateFolderRequest
from openapi_client.models.update_folder_response import UpdateFolderResponse
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
    api_instance = openapi_client.FolderApi(api_client)
    folder_id = 'FAF2lZtloor' # str | The folder ID.
    update_folder_request = openapi_client.UpdateFolderRequest() # UpdateFolderRequest | 

    try:
        api_response = api_instance.update_folder(folder_id, update_folder_request)
        print("The response of FolderApi->update_folder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FolderApi->update_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **str**| The folder ID. | 
 **update_folder_request** | [**UpdateFolderRequest**](UpdateFolderRequest.md)|  | 

### Return type

[**UpdateFolderResponse**](UpdateFolderResponse.md)

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

