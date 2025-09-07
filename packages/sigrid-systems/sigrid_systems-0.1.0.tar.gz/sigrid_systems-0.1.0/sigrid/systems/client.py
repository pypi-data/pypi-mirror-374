"""
SIGRID Systems Client

Google-style clean client interface for SIGRID legal analysis.
"""

import httpx
import json
import asyncio
import uuid
from typing import List, Dict, Any, Optional, AsyncIterator, Union

from .exceptions import (
    from_http_status, 
    NetworkError,
    SigridError,
    ClientError,
    ServerError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)
from .types import Document, AnalysisEvent, AnalysisRequest, ClientConfig, Documents, Events, RawEvents
from .stream import AnalysisStream

# Make exceptions available at module level
__all__ = [
    "Client",
    "SigridError",
    "ClientError", 
    "ServerError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NetworkError",
]


class Client:
    """
    SIGRID Legal Analysis API Client.
    
    Google-style clean interface with automatic error handling and retries.
    
    Usage:
        from sigrid import systems
        
        client = systems.Client(
            api_key="your-key",
            tenant_id="your-tenant", 
            user_id="user-123"
        )
        
        # Stream analysis results
        for event in client.analyze_stream(documents, query):
            print(event)
            
        # Get all results at once
        results = client.analyze(documents, query)
    """
    
    def __init__(
        self,
        *,
        api_key: str,
        user_id: str,
        config: Optional[ClientConfig] = None
    ):
        """
        Initialize SIGRID client.
        
        Args:
            api_key: Your tenant-specific API subscription key
            user_id: User identifier to act on behalf of
            config: Optional client configuration
        """
        if not all([api_key, user_id]):
            raise ValueError("api_key and user_id are required")
            
        self._config = config or ClientConfig()
        
        self._headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "X-User-Id": user_id,
            "X-On-Behalf-Of-User": user_id,
            "Content-Type": "application/json",
        }
    
    async def analyze(
        self,
        documents: Documents,
        query: str,
        *,
        include_reasoning: bool = True,
        correlation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> List[AnalysisEvent]:
        """
        Analyze documents and return all events.
        
        Args:
            documents: List of documents to analyze
            query: Analysis query
            include_reasoning: Include reasoning in results
            correlation_id: Optional correlation ID
            idempotency_key: Optional idempotency key
            
        Returns:
            List of all analysis events
        """
        events = []
        async for event in self.analyze_stream(
            documents=documents,
            query=query,
            include_reasoning=include_reasoning,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key
        ):
            events.append(event)
        return events
    
    def analyze_stream(
        self,
        documents: Documents,
        query: str,
        *,
        include_reasoning: bool = True,
        correlation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> AnalysisStream:
        """
        Analyze documents with streaming results using context manager.
        
        Args:
            documents: List of documents to analyze
            query: Analysis query
            include_reasoning: Include reasoning in results
            correlation_id: Optional correlation ID
            idempotency_key: Optional idempotency key
            
        Returns:
            AnalysisStream context manager
        """
        # Convert documents to proper format
        doc_list = []
        for doc in documents:
            if isinstance(doc, Document):
                doc_list.append(doc.to_dict())
            elif isinstance(doc, dict):
                doc_list.append(doc)
            else:
                raise ValueError(f"Document must be Document instance or dict, got {type(doc)}")
        
        request = AnalysisRequest(
            documents=[Document.from_dict(d) for d in doc_list],
            query=query,
            include_reasoning=include_reasoning,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key
        )
        
        raw_stream = self._stream_analysis(request)
        return AnalysisStream(raw_stream)
    
    async def get_session_log(
        self, 
        session_id: str, 
        *,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get session log by ID.
        
        Args:
            session_id: Session identifier
            correlation_id: Optional correlation ID
            
        Returns:
            Session log data
        """
        headers = self._headers.copy()
        if correlation_id:
            headers["X-Correlation-Id"] = correlation_id
            
        response = await self._request(
            "GET", 
            f"/v1/analysis/sigrid/logs/session/{session_id}",
            headers=headers
        )
        return response.json()
    
    async def get_user_logs(self, *, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all logs for the current user.
        
        Args:
            correlation_id: Optional correlation ID
            
        Returns:
            User logs data
        """
        headers = self._headers.copy()
        if correlation_id:
            headers["X-Correlation-Id"] = correlation_id
            
        user_id = self._headers["X-User-Id"]
        response = await self._request(
            "GET",
            f"/v1/analysis/sigrid/logs/user/{user_id}", 
            headers=headers
        )
        return response.json()
    
    async def _stream_analysis(self, request: AnalysisRequest) -> RawEvents:
        """Internal method to stream raw analysis events."""
        headers = self._headers.copy()
        headers["Accept"] = "text/event-stream"
        
        if request.correlation_id:
            headers["X-Correlation-Id"] = request.correlation_id
        # Always add idempotency key - generate if not provided    
        idempotency_key = request.idempotency_key or f"sigrid-{uuid.uuid4()}"
        headers["Idempotency-Key"] = idempotency_key
            
        payload = {
            "documents": [doc.to_dict() for doc in request.documents],
            "query": request.query,
            "streaming": True,
            "include_reasoning": request.include_reasoning
        }
        
        url = f"{self._config.base_url}/v1/analysis/sigrid/analyze"
        
        try:
            async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                async with client.stream(
                    "POST", 
                    url, 
                    json=payload, 
                    headers=headers
                ) as response:
                    self._raise_for_status(response)
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data = line[len("data:"):].strip()
                            if data:
                                try:
                                    yield json.loads(data)
                                except json.JSONDecodeError:
                                    # Skip invalid JSON lines
                                    continue
                                    
        except httpx.RequestError as e:
            raise NetworkError(f"Network error during streaming: {e}", cause=e)
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        url = f"{self._config.base_url}{endpoint}"
        last_exception = None
        
        for attempt in range(self._config.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    headers=self._headers, 
                    timeout=self._config.timeout
                ) as client:
                    response = await client.request(method, url, **kwargs)
                    self._raise_for_status(response)
                    return response
                    
            except httpx.HTTPStatusError as e:
                if not self._should_retry(e.response.status_code, attempt):
                    self._raise_for_status(e.response)
                last_exception = e
                
            except httpx.RequestError as e:
                if attempt >= self._config.max_retries:
                    raise NetworkError(f"Request failed after {self._config.max_retries} retries: {e}", cause=e)
                last_exception = e
                
            # Exponential backoff
            if attempt < self._config.max_retries:
                sleep_time = self._config.retry_backoff ** attempt
                await asyncio.sleep(sleep_time)
        
        # Should not reach here, but fallback
        if last_exception:
            raise last_exception
        raise NetworkError("Request failed due to unknown error")
    
    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Determine if request should be retried."""
        if attempt >= self._config.max_retries:
            return False
        # Retry on server errors (5xx) and rate limits (429)
        return status_code >= 500 or status_code == 429
    
    def _raise_for_status(self, response: httpx.Response) -> None:
        """Raise appropriate exception for HTTP status."""
        if response.is_success:
            return
            
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status_code = response.status_code
            message = f"HTTP {status_code} error"
            response_body = response.text
            
            # Try to extract error message from response
            try:
                error_data = response.json()
                if "message" in error_data:
                    message = error_data["message"]
                elif "error" in error_data:
                    message = error_data["error"]
            except (json.JSONDecodeError, ValueError):
                pass
            
            raise from_http_status(
                status_code, 
                message, 
                response_body=response_body,
                cause=e
            )