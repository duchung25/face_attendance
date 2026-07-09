from pydantic import BaseModel
from datetime import datetime
from app.schemas.user_schema import UserResponse


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    check_in: datetime
    user: UserResponse | None = None

    class Config:
        from_attributes = True
