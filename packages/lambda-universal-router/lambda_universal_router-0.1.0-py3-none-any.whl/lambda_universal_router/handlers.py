from typing import Any, Dict
from .base import EventHandler, BaseEvent
from .events import APIGatewayEvent, SQSEvent, S3Event

class APIGatewayHandler(EventHandler):
    """Handler for API Gateway events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'httpMethod' in event and
            'path' in event and
            'requestContext' in event
        )
    
    def parse_event(self, event: Dict[str, Any]) -> APIGatewayEvent:
        return APIGatewayEvent(event)

class SQSHandler(EventHandler):
    """Handler for SQS events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'eventSource' in event['Records'][0] and
            event['Records'][0]['eventSource'] == 'aws:sqs'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> SQSEvent:
        return SQSEvent(event)

class S3Handler(EventHandler):
    """Handler for S3 events."""
    
    def can_handle(self, event: Dict[str, Any]) -> bool:
        return (
            'Records' in event and
            len(event['Records']) > 0 and
            'eventSource' in event['Records'][0] and
            event['Records'][0]['eventSource'] == 'aws:s3'
        )
    
    def parse_event(self, event: Dict[str, Any]) -> S3Event:
        return S3Event(event)
