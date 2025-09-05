"""
Kadoa SDK for Python.

A Python SDK for interacting with the Kadoa API.
"""

from kadoa_sdk.app import (
    initialize_app,
    get_config,
    get_http_client,
    dispose,
    KadoaApp,
    KadoaConfig,
)

from kadoa_sdk.extraction import (
    run_extraction,
    ExtractionOptions,
    ExtractionResult,
    NavigationMode,
    Location,
    WorkflowStatus,
)

from kadoa_sdk.exceptions import KadoaSdkException, KadoaHttpException, KadoaErrorCode

from kadoa_sdk.events import (
    KadoaEvent,
    KadoaEventName,
    AnyKadoaEvent,
    KadoaEventEmitter,
)

__version__ = "0.3.1"

__all__ = [
    # App functions
    "initialize_app",
    "get_config",
    "get_http_client",
    "dispose",
    # App types
    "KadoaApp",
    "KadoaConfig",
    # Extraction functions
    "run_extraction",
    # Extraction types
    "ExtractionOptions",
    "ExtractionResult",
    "NavigationMode",
    "Location",
    "WorkflowStatus",
    # Exceptions
    "KadoaSdkException",
    "KadoaHttpException",
    "KadoaErrorCode",
    # Events
    "KadoaEvent",
    "KadoaEventName",
    "AnyKadoaEvent",
    "KadoaEventEmitter",
]
