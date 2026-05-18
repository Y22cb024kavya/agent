import json
import os

from groq import AsyncGroq

SYSTEM_PROMPT = """
You are an internal Scheduling Extraction Agent for a Human-in-the-Loop system.
Your job is to read short, often sloppy text messages from employees and extract the scheduling details.

You MUST respond ONLY with a valid JSON object. Do not include markdown formatting like ```json.

RULES:
1. Extract the 'client_id'. It is usually a sequence of numbers or letters following words like "meet", "id", or "client".
2. Extract the 'time' and format it strictly as a 12-hour AM/PM string (e.g., "4:00 PM").
3. Determine the 'intent'. If they are approving a meeting, intent is "schedule_meeting". If they are rejecting or saying something else, intent is "other".
4. If either the time or the client_id is missing or ambiguous, set "status" to "failed" and provide an "error_message". Otherwise, status is "success".

EXPECTED JSON OUTPUT FORMAT:
{
    "intent": "schedule_meeting" | "other",
    "client_id": "extracted string",
    "time": "formatted time string",
    "status": "success" | "failed",
    "error_message": "null if success, string if failed"
}
"""

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


async def extract_meeting_details(employee_message: str) -> dict:
    try:
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": employee_message},
            ],
            model="llama3-8b-8192",
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as exc:
        print(f"LLM Error: {exc}")
        return {
            "intent": "other",
            "client_id": None,
            "time": None,
            "status": "failed",
            "error_message": "Agent failed to process the message.",
        }
