"""
SIGRID - Legal Analysis API Client Library

HTTP client library for the SIGRID legal analysis platform with structured 
error handling, automatic retry logic, and real-time streaming analysis.

Usage:
    from sigrid.systems import client, types, exceptions
    
    try:
        api_client = client.Client(api_key="your-key", user_id="user-123")
        doc = types.Document(id="case_1", content="ECHR case content...")
        
        Stream analysis results (5-15 minutes)
        async with api_client.analyze_stream([doc], "Article 8 violation?") as stream:
            async for event in stream:
                if event.type == "sigrid_systems_response":
                    route = event.data.get("route")
                    if route == "sigrid_systems_reasoning":
                        print(f"Reasoning: {event.data['reasoning']}")
                    elif route == "sigrid_system_analysis":
                        print(f"Analysis: {event.data['response']}")
        
        Get audit logs
        session_logs = await api_client.get_session_log(session_id)
        
    except exceptions.ValidationError as e:
        print(f"Input validation failed: {e}")
    except exceptions.AuthenticationError:
        print("Check your API key")

Limits:
    - Max 20 documents per request
    - Max 500KB per document
    - Max 5MB total size
    - Max 5000 char query length

Error Codes:
    400: Validation error    401: Missing auth headers
    403: Auth failure        422: Size limits exceeded  
    429: Rate limited        500: Server error
    504: Analysis timeout

Data Hygiene:
    All user documents automatically purged after analysis completion.
    GDPR compliant with configurable retention (default 6 months for logs).
"""

__version__ = "0.1.1"

from . import systems

__all__ = ["systems"]