from pydantic import BaseModel, Field, constr
from enum import Enum
from app.models.core import DateTimeModelMixin, IDModelMixin
from app.models.insurance import InsurancePublic
from app.models.roles import RolePublic
import datetime
from typing import Optional, List

class VehicleType(str, Enum):
    bicycle = "bicycle"
    motorcycle = "motorcycle"
    car = "car"
    truck = "truck"
    bus = "bus"


class VehiclesModel(BaseModel):
    """
    ...
    """
    sign: Optional[str]
    type: Optional[VehicleType] = "car"
    model: Optional[str]
    manufacture_year: Optional[int] = Field(..., gt=1970, le = datetime.date.today().year)


class VehiclesInDB(VehiclesModel, IDModelMixin, DateTimeModelMixin):
    sign: str
    type: VehicleType
    model: str
    manufacture_year: int = Field(..., gt=1970, le = datetime.date.today().year)


class VehiclesCreate(VehiclesModel):
    sign: constr(min_length=3, regex="[a-zA-Z0-9_-]+$")
    type: VehicleType
    model: str
    manufacture_year: int = Field(..., gt=1970, le = datetime.date.today().year)

# class VehiclesUpdate(VehiclesModel):
#     pass

class VehiclesPublic(VehiclesModel, IDModelMixin, DateTimeModelMixin):
    insurance: Optional[InsurancePublic]
    roles: Optional[RolePublic]

