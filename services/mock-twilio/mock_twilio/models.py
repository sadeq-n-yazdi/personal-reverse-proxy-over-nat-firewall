"""Data models for the mock Twilio API."""

import time
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SMSMessage(BaseModel):
    """Model representing a Twilio SMS message."""
    
    sid: str = Field(default_factory=lambda: f"SM{uuid.uuid4().hex}")
    account_sid: str
    to: str
    from_: str = Field(alias="from")
    body: str
    status: str = "queued"
    direction: str = "outbound-api"
    date_created: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    price: Optional[str] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        """Pydantic model configuration."""
        
        populate_by_name = True


class SMSMessageRequest(BaseModel):
    """Model for the SMS message request body."""
    
    To: str
    From: str
    Body: str
    
    
class SMSMessageResponse(BaseModel):
    """Model for the SMS message response."""
    
    sid: str
    date_created: str
    date_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    date_sent: Optional[str] = None
    account_sid: str
    to: str
    from_: str = Field(alias="from")
    body: str
    status: str
    num_segments: str = "1"
    num_media: str = "0"
    direction: str
    api_version: str = "2010-04-01"
    price: Optional[str] = None
    price_unit: str = "USD"
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    uri: str
    
    class Config:
        """Pydantic model configuration."""
        
        populate_by_name = True


class LogEntry(BaseModel):
    """Model for log entries."""
    
    timestamp: float = Field(default_factory=time.time)
    message_sid: str
    to: str
    from_: str = Field(alias="from")
    body: str
    status: str


class MessageStore:
    """In-memory store for messages and logs."""
    
    def __init__(self):
        """Initialize an empty message store."""
        self.messages: List[SMSMessage] = []
        self.logs: List[LogEntry] = []
    
    def add_message(self, message: SMSMessage) -> None:
        """Add a message to the store."""
        self.messages.append(message)
        
        # Also add to logs
        log_entry = LogEntry(
            message_sid=message.sid,
            to=message.to,
            from_=message.from_,
            body=message.body,
            status=message.status,
        )
        self.logs.append(log_entry)
    
    def get_logs(self) -> List[LogEntry]:
        """Return all logs."""
        return sorted(self.logs, key=lambda x: x.timestamp, reverse=True)


# Global store instance
message_store = MessageStore()