from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None
    role_name: str
    department: str | None
    is_active: bool
    created_at: datetime
    last_login: datetime | None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = None
    role_id: int | None = None
    department: str | None = None
    is_active: bool | None = None


class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}
