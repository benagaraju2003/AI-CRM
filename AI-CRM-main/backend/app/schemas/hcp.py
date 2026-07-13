from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class HCPBase(BaseModel):
    name: str
    hospital: Optional[str] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPRead(HCPBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
