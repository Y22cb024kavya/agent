from typing import Literal

from pydantic import BaseModel, Field


class EmployeeMessageRequest(BaseModel):
    employee_phone: str | None = Field(default=None, description="Employee WhatsApp number.")
    message: str = Field(..., min_length=1, description="Raw employee message.")


class MeetingExtractionResult(BaseModel):
    intent: Literal["schedule_meeting", "other"]
    client_id: str | None = None
    time: str | None = None
    status: Literal["success", "failed"]
    error_message: str | None = None


class SendMessageRequest(BaseModel):
    to: str = Field(..., min_length=1, description="Destination WhatsApp number.")
    body: str = Field(..., min_length=1, description="Message body.")
