# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from openapi_client.api.app_api import AppApi
    from openapi_client.api.asset_api import AssetApi
    from openapi_client.api.autofill_api import AutofillApi
    from openapi_client.api.brand_template_api import BrandTemplateApi
    from openapi_client.api.comment_api import CommentApi
    from openapi_client.api.connect_api import ConnectApi
    from openapi_client.api.design_api import DesignApi
    from openapi_client.api.design_import_api import DesignImportApi
    from openapi_client.api.export_api import ExportApi
    from openapi_client.api.folder_api import FolderApi
    from openapi_client.api.oauth_api import OauthApi
    from openapi_client.api.resize_api import ResizeApi
    from openapi_client.api.user_api import UserApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from openapi_client.api.app_api import AppApi
from openapi_client.api.asset_api import AssetApi
from openapi_client.api.autofill_api import AutofillApi
from openapi_client.api.brand_template_api import BrandTemplateApi
from openapi_client.api.comment_api import CommentApi
from openapi_client.api.connect_api import ConnectApi
from openapi_client.api.design_api import DesignApi
from openapi_client.api.design_import_api import DesignImportApi
from openapi_client.api.export_api import ExportApi
from openapi_client.api.folder_api import FolderApi
from openapi_client.api.oauth_api import OauthApi
from openapi_client.api.resize_api import ResizeApi
from openapi_client.api.user_api import UserApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
