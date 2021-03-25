from pydantic import BaseModel
from app.models.core import DateTimeModelMixin, IDModelMixin
from app.models.vehicles import VehiclesPublic
from app.models.users import ProfilePublic
from app.models.accident_statement import Accident_statement_Public
from app.models.temporary_accident_driver_data import Temporary_Data_Public
from datetime import date, datetime
from typing import Optional


class AccidentModel(BaseModel):
    date: Optional[datetime]
    city_id: Optional[int]
    address: Optional[str]
    injuries: Optional[str]
    road_problems: Optional[str]
    closed_case: bool = False


class AccidentInDB(AccidentModel, IDModelMixin, DateTimeModelMixin):
    date: datetime
    city_id: int
    address: str
    closed_case: bool

class AccidentCreate(AccidentModel):
    date: datetime
    city_id: int
    address: str



class AccidentPublic(AccidentModel, IDModelMixin, DateTimeModelMixin):
    accident_statement: Optional[Accident_statement_Public]


