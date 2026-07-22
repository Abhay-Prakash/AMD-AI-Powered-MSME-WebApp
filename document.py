from uuid import UUID
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: UUID
    client_id: UUID
    filename: str
    file_type: str
    uploaded_at: str | None
