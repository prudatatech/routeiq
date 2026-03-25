from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenData(BaseModel):
    user_id: str
    role: str = "driver"
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
