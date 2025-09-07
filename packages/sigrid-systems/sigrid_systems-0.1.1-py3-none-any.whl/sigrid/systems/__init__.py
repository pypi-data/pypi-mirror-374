"""
SIGRID Systems - HTTP client modules for legal analysis API

Modules:
    client - HTTP client with streaming and batch analysis
    types - Data structures (Document, ClientConfig, AnalysisEvent)  
    exceptions - Error handling (AuthenticationError, ValidationError, etc.)

Usage:
    from sigrid.systems import client, types, exceptions
"""

from . import client, types, exceptions

__all__ = [
    "client",
    "types", 
    "exceptions",
]