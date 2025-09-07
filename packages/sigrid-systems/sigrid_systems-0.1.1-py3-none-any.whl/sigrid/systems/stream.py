"""
SIGRID Systems Streaming

Context manager for streaming analysis results.
"""

import json
from typing import AsyncIterator, Optional, Dict, Any
from .types import AnalysisEvent
from .exceptions import ValidationError

# Type alias to avoid forward reference issues
RawEvents = AsyncIterator[Dict[str, Any]]


class AnalysisStream:
    """Context manager for streaming analysis results."""
    
    def __init__(self, raw_stream: RawEvents):
        self._raw_stream = raw_stream
        self._events: Optional[AsyncIterator[AnalysisEvent]] = None
    
    async def __aenter__(self):
        """Enter the context manager."""
        return self
    
    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Exit the context manager - cleanup resources."""
        # Clean up any resources if needed
        pass
    
    def __aiter__(self):
        """Make the stream iterable."""
        return self._events_iterator()
    
    async def _events_iterator(self) -> AsyncIterator[AnalysisEvent]:
        """Convert raw events to AnalysisEvent objects with validation."""
        async for raw_event in self._raw_stream:
            if raw_event is None:
                continue  # Skip null events
            
            try:
                yield AnalysisEvent.from_dict(raw_event)
            except (ValidationError, ValueError, TypeError) as e:
                # Log but don't break the stream for invalid events
                continue