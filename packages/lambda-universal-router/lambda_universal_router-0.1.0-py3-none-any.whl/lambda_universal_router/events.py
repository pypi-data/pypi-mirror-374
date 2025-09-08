from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from .base import BaseEvent

@dataclass
class APIGatewayRequestContext:
    http_method: str
    path: str
    stage: str
    request_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIGatewayRequestContext':
        return cls(
            http_method=data.get('httpMethod', ''),
            path=data.get('path', ''),
            stage=data.get('stage', ''),
            request_id=data.get('requestId', '')
        )

class APIGatewayEvent(BaseEvent):
    """Represents an API Gateway event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.http_method = event_dict.get('httpMethod', '')
        self.path = event_dict.get('path', '')
        self.headers = event_dict.get('headers', {})
        self.query_string_parameters = event_dict.get('queryStringParameters', {})
        self.path_parameters = event_dict.get('pathParameters', {})
        self.body = event_dict.get('body', '')
        self.request_context = APIGatewayRequestContext.from_dict(
            event_dict.get('requestContext', {})
        )

@dataclass
class SQSMessage:
    """Represents a single SQS message."""
    message_id: str
    body: str
    attributes: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SQSMessage':
        return cls(
            message_id=data.get('messageId', ''),
            body=data.get('body', ''),
            attributes=data.get('messageAttributes', {})
        )

class SQSEvent(BaseEvent):
    """Represents an SQS event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            SQSMessage.from_dict(record)
            for record in event_dict.get('Records', [])
        ]

@dataclass
class S3Object:
    """Represents an S3 object in the event."""
    key: str
    size: int
    etag: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'S3Object':
        return cls(
            key=data.get('key', ''),
            size=data.get('size', 0),
            etag=data.get('eTag', '')
        )

@dataclass
class S3Bucket:
    """Represents an S3 bucket in the event."""
    name: str
    arn: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'S3Bucket':
        return cls(
            name=data.get('name', ''),
            arn=data.get('arn', '')
        )

@dataclass
class S3Record:
    """Represents a single S3 record in the event."""
    event_name: str
    event_time: str
    bucket: S3Bucket
    object: S3Object
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'S3Record':
        s3_data = data.get('s3', {})
        return cls(
            event_name=data.get('eventName', ''),
            event_time=data.get('eventTime', ''),
            bucket=S3Bucket.from_dict(s3_data.get('bucket', {})),
            object=S3Object.from_dict(s3_data.get('object', {}))
        )

class S3Event(BaseEvent):
    """Represents an S3 event."""
    
    def _parse_event(self, event_dict: Dict[str, Any]) -> None:
        self.records = [
            S3Record.from_dict(record)
            for record in event_dict.get('Records', [])
        ]
