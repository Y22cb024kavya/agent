import os

from appwrite.client import Client
from appwrite.id import ID
from appwrite.services.databases import Databases

appwrite_client = Client()
appwrite_client.set_endpoint(
    os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
)
appwrite_client.set_project(os.getenv("APPWRITE_PROJECT_ID", ""))
appwrite_client.set_key(os.getenv("APPWRITE_API_KEY", ""))

databases = Databases(appwrite_client)

DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "")
COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID", "")


async def upsert_meeting_request(
    employee_phone: str | None,
    client_id: str | None,
    meeting_time: str | None,
    source_message: str,
) -> None:
    if not DATABASE_ID or not COLLECTION_ID:
        return

    payload = {
        "employee_phone": employee_phone,
        "client_id": client_id,
        "meeting_time": meeting_time,
        "source_message": source_message,
        "status": "pending_confirmation",
    }

    databases.create_document(
        database_id=DATABASE_ID,
        collection_id=COLLECTION_ID,
        document_id=ID.unique(),
        data=payload,
    )
