from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr
from app.models.core import DateTimeModelMixin,IDModelMixin

class Temporary_Data_Base(BaseModel):
    driver_full_name: Optional[str]
    driver_email: Optional[EmailStr]
    vehicle_sign: Optional[str]
    insurance_number: Optional[str]
    insurance_email: Optional[EmailStr]
    answered: bool = False


class Temporary_Data_Create(Temporary_Data_Base):
    accident_id: int
    driver_full_name: str
    driver_email: EmailStr
    vehicle_sign: str
    insurance_number: str
    insurance_email: EmailStr

# class Temporary_Data_Update(Temporary_Data_Base):
#     answered: bool

class Temporary_Data_Update(Temporary_Data_Base):
    driver_full_name: Optional[str]
    driver_email: Optional[EmailStr]
    vehicle_sign: Optional[str]
    insurance_number: Optional[str]
    insurance_email: Optional[EmailStr]

class Temporary_Data_InDB(IDModelMixin, DateTimeModelMixin, Temporary_Data_Base):
    accident_id: int
    driver_full_name: str
    driver_email: EmailStr
    vehicle_sign: str
    insurance_number: str
    insurance_email: EmailStr
    answered: bool


class Temporary_Data_Public(Temporary_Data_InDB):
    pass