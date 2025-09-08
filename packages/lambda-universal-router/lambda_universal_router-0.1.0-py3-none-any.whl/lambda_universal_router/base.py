from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, TypeVar, Generic

T = TypeVar('T')

class BaseEvent(Generic[T]):
    """Base class for all Lambda events."""
    
    def __init__(self, event_dict: Dict[str, Any]):
        self._raw_event = event_dict
        self._parse_event(event_dict)
    
    @abstractmethod
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        """Parse the raw event dictionary into structured data."""
        pass
    
    @property
    def raw_event(self) -> Dict[str, Any]:
        """Get the raw event dictionary."""
        return self._raw_event

class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    def can_handle(self, event: Dict[str, Any]) -> bool:
        """Check if this handler can process the given event."""
        pass
    
    @abstractmethod
    def parse_event(self, event: Dict[str, Any]) -> BaseEvent:
        """Parse the raw event into a structured event object."""
        pass

class HandlerRegistration:
    """Stores information about a registered handler function."""
    
    def __init__(
        self,
        func: Callable,
        handler: EventHandler,
        path: Optional[str] = None,
        method: Optional[str] = None
    ):
        self.func = func
        self.handler = handler
        self.path = path
        self.method = method
