"""
SIGRID - Legal Analysis API Client Library

Clean, Google-style interface for the SIGRID legal analysis platform.

Basic usage:
    from sigrid import systems
    
    client = systems.Client(
        api_key="your-key",
        tenant_id="your-tenant",
        user_id="user-123"
    )
    
    results = client.analyze(documents, query)
"""

__version__ = "0.1.0"

from . import systems

__all__ = ["systems"]