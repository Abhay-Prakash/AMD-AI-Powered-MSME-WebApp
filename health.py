from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str
    migration_version: str | None = None
    service: str
