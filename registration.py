from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegistrationCreate(BaseModel):
    role: str = Field(..., pattern="^(business_owner|ca)$")
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    phone: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8)
    company_name: Optional[str] = Field(None, max_length=255)
    udyam_number: Optional[str] = Field(None, max_length=100)
    icai_membership_number: Optional[str] = Field(None, max_length=100)
    firm_name: Optional[str] = Field(None, max_length=255)

class RegistrationResponse(BaseModel):
    id: str
    email: str
    role: str
    registration_status: str

    class Config:
        from_attributes = True
