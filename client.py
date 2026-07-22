from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class ClientBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    owner_name: str | None = Field(default=None, max_length=255)
    gst_number: str | None = Field(default=None, max_length=15)
    pan_number: str | None = Field(default=None, max_length=10)
    udyam_number: str | None = Field(default=None, max_length=50)
    sector: str | None = Field(default=None, max_length=100)
    enterprise_class: str | None = Field(default=None, max_length=50)
    state: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    turnover: Decimal | None = Field(default=None, ge=0)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)

class ClientRead(ClientBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
