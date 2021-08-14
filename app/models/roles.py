from typing import Optional
from enum import Enum
from pydantic import BaseModel
from app.models.core import DateTimeModelMixin,IDModelMixin

class RoleType(str, Enum):
    Owner = "owner"
    User = "user"
    NotUser = "not a user anymore"

class RoleBase(BaseModel):
    role: Optional[RoleType] = "owner"


class RoleCreate(RoleBase):

    user_id: int
    vehicle_id: int


class RoleUpdate(RoleBase):
   role: Optional[RoleType] 


class RoleInDB(IDModelMixin, DateTimeModelMixin, RoleBase):
    user_id: int
    vehicle_id: int
    role: RoleType 


class RolePublic(RoleInDB):
    pass


