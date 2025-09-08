from typing import Any, Dict, List, Optional, Callable
from .base import EventHandler, HandlerRegistration, BaseEvent
from .handlers import APIGatewayHandler, SQSHandler, S3Handler

class Router:
    """Main router class that handles Lambda event routing."""
    
    def __init__(self):
        self._handlers: List[HandlerRegistration] = []
        self._event_handlers = {
            'apigateway': APIGatewayHandler(),
            'sqs': SQSHandler(),
            's3': S3Handler()
        }
    
    def apigateway(self, path: str, method: str = "GET") -> Callable:
        """Decorator for API Gateway event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['apigateway'],
                    path=path,
                    method=method.upper()
                )
            )
            return func
        return decorator
    
    def sqs(self) -> Callable:
        """Decorator for SQS event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['sqs']
                )
            )
            return func
        return decorator
    
    def s3(self) -> Callable:
        """Decorator for S3 event handlers."""
        def decorator(func: Callable) -> Callable:
            self._handlers.append(
                HandlerRegistration(
                    func=func,
                    handler=self._event_handlers['s3']
                )
            )
            return func
        return decorator
    
    def dispatch(self, event: Dict[str, Any], context: Any) -> Any:
        """Dispatch the event to the appropriate handler."""
        for registration in self._handlers:
            if registration.handler.can_handle(event):
                parsed_event = registration.handler.parse_event(event)
                return registration.func(parsed_event, context)
        
        raise ValueError("No handler found for the given event type")
