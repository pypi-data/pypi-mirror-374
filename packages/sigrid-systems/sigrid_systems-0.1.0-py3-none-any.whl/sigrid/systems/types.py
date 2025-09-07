"""
SIGRID Systems Types

Google-style type definitions and data structures.
"""

from typing import Dict, List, Any, Optional, Union, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from .exceptions import ValidationError


@dataclass(frozen=True)
class Document:
    """Represents a legal document for analysis."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create Document from dictionary. Raises ValidationError on missing fields."""
        try:
            return cls(
                id=data["id"],
                content=data["content"],
                metadata=data.get("metadata", {})
            )
        except KeyError as e:
            raise ValidationError(f"Invalid response from server: missing required field '{e.args[0]}' in Document object.") from e
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Document to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }


@dataclass 
class AnalysisRequest:
    """Analysis request configuration."""
    documents: List[Document]
    query: str
    include_reasoning: bool = True
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class AnalysisEvent:
    """Event received during streaming analysis."""
    type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisEvent":
        """Create AnalysisEvent from dictionary."""
        return cls(
            type=data.get("type", "unknown"),
            data=data,  # Use the whole event as data
            timestamp=data.get("timestamp")
        )


@dataclass
class ClientConfig:
    """Client configuration options."""
    base_url: str = "https://sigrid-systems.com"
    timeout: int = 1200  # Match backend timeout (20 minutes)
    max_retries: int = 3
    retry_backoff: float = 2.0


class EventType(Enum):
    """Analysis event types."""
    STARTED = "analysis_started"
    PROGRESS = "analysis_progress" 
    RESULT = "analysis_result"
    COMPLETED = "analysis_completed"
    ERROR = "analysis_error"


# Type aliases for convenience
Documents = List[Union[Document, Dict[str, Any]]]
Events = AsyncIterator[AnalysisEvent]
RawEvents = AsyncIterator[Dict[str, Any]]