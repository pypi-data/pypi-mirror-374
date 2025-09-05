"""
API client helper functions for Kadoa SDK.
"""

from weakref import WeakKeyDictionary
from typing import TYPE_CHECKING

from openapi_client import CrawlApi, WorkflowsApi, ApiClient

if TYPE_CHECKING:
    from kadoa_sdk.app import KadoaApp


# Use WeakKeyDictionary for automatic garbage collection
_crawl_api_cache: WeakKeyDictionary["KadoaApp", CrawlApi] = WeakKeyDictionary()
_workflows_api_cache: WeakKeyDictionary["KadoaApp", WorkflowsApi] = WeakKeyDictionary()


def get_crawl_api(app: "KadoaApp") -> CrawlApi:
    """
    Get or create a CrawlApi instance for the given app.

    Uses WeakKeyDictionary to cache instances, preventing memory leaks.

    Args:
        app: The KadoaApp instance

    Returns:
        CrawlApi instance
    """
    if app not in _crawl_api_cache:
        api_client = ApiClient(configuration=app.configuration)
        _crawl_api_cache[app] = CrawlApi(api_client)

    return _crawl_api_cache[app]


def get_workflows_api(app: "KadoaApp") -> WorkflowsApi:
    """
    Get or create a WorkflowsApi instance for the given app.

    Uses WeakKeyDictionary to cache instances, preventing memory leaks.

    Args:
        app: The KadoaApp instance

    Returns:
        WorkflowsApi instance
    """
    if app not in _workflows_api_cache:
        api_client = ApiClient(configuration=app.configuration)
        _workflows_api_cache[app] = WorkflowsApi(api_client)

    return _workflows_api_cache[app]
