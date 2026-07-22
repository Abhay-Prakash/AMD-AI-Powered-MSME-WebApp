from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: UUID
    title: str
    message: str
    notification_type: str
    priority: str
    is_read: bool
    created_at: str

class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: list[NotificationResponse]
