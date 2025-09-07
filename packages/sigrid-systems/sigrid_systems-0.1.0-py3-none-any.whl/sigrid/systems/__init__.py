"""
SIGRID Systems - Main client interface

Google-style clean interface for SIGRID legal analysis.

Usage:
    from sigrid.systems import Client, Document
    
    api_client = Client(api_key="...", user_id="...")
    async with api_client.analyze_stream(documents, query) as stream:
        async for event in stream:
            print(event.type, event.data)
"""

from .client import Client
from .types import Document, AnalysisRequest, AnalysisEvent, EventType
from .exceptions import (
    SigridError,
    ClientError,
    ServerError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError
)

__all__ = [
    "Client",
    "Document",
    "AnalysisRequest",
    "AnalysisEvent",
    "EventType",
    "SigridError",
    "ClientError",
    "ServerError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
]