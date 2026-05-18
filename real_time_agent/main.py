import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from agent.llm_processor import extract_meeting_details
from models.schemas import (
    EmployeeMessageRequest,
    MeetingExtractionResult,
    SendMessageRequest,
)
from services.appwrite_db import upsert_meeting_request
from services.whatsapp_api import send_whatsapp_message

load_dotenv()

app = FastAPI(title="Real Time Agent")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/webhooks/employee-message", response_model=MeetingExtractionResult)
async def employee_message_webhook(
    payload: EmployeeMessageRequest,
) -> MeetingExtractionResult:
    extraction = await extract_meeting_details(payload.message)
    result = MeetingExtractionResult(**extraction)

    if result.status == "success":
        await upsert_meeting_request(
            employee_phone=payload.employee_phone,
            client_id=result.client_id,
            meeting_time=result.time,
            source_message=payload.message,
        )
        return result

    if payload.employee_phone:
        await send_whatsapp_message(
            SendMessageRequest(
                to=payload.employee_phone,
                body=(
                    "I couldn't find the Client ID or time. "
                    "Please reply with 'Meet [ID] at [Time]'."
                ),
            )
        )

    return result


@app.post("/messages/send")
async def send_message(payload: SendMessageRequest) -> dict:
    delivered = await send_whatsapp_message(payload)
    if not delivered:
        raise HTTPException(status_code=502, detail="Failed to send WhatsApp message.")

    return {"status": "sent"}
