from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, validator
from app.models.core import DateTimeModelMixin,IDModelMixin
from app.models.vehicles import VehiclesPublic
from app.models.users import ProfilePublic
from app.models.roles import RolePublic
from app.models.insurance import InsurancePublic
from app.models.accident_statement_sketch import Only_Sketch
from app.models.accident_image import Accident_Image_Public

class BytesBaseModel(BaseModel):
    @validator('*')
    def change_bytea_to_bytes(cls, v, values, config, field):
        if field.outer_type_ is bytes and v:
            return str(v).encode()
        return v


class CausedByType(str, Enum):
    AddCause="add cause"
    HitWhenVehicleWasParked = "hit when was parked"
    HitWhenVehicleWasExitingParking = "hit when was exiting parking spot"
    HitWhenVehicleWasEnteringParking = "was entering parking spot"
    HitWhenVehicleWasParking = "while was parking"
    HitWhenVehicleWithItsDoorOpen = "had door open"
    HitWhenVehicleWasEnteringTrafficCircle = "was entering traffic circle"
    HitWhenVehicleWasDrivinTrafficCircle = "was driving traffic circle"
    HitWhenVehicleSameDirectionSameLaneRearEnd = "rear-end vehicle accident while was driving in the same lane"
    HitWhenVehicleWhileChangingSameDirectionDifferentLane = "accident while was driving in the different lane"
    HitWhenVehicleWhenChangedLane = "changed lane"
    HitWhenVehicleWhenOvertook = "overtook"
    HitWhenVehicleWhenTurntLeft = "turnt left"
    HitWhenVehicleWhenTurntRight = "turnt right"
    HitWhenVehicleWhenWentBackwards = "went backwards"
    HitWhenVehicleWhenWentWrongdirection = "went wrong direction"
    HitWhenVehicleWhenWasDrivingRightInCrossjunction = "drove on the right in the cross junction"
    HitWhenVehicleWhenIgnoredSign = "ignored sign"
    HitWhenVehicleWhenIgnoredRedLight = "ignored red light"

class Accident_statement_Base(BaseModel):
    caused_by: Optional[CausedByType]
    comments: Optional[str]

class Accident_statement_Create(Accident_statement_Base):

    user_id: int
    vehicle_id: int
    accident_id: int
    insurance_id: int
    role_id:int
    done: bool = False

class Accident_statement_Update(Accident_statement_Base):
    pass


class Accident_Statement_Detection_Update(BaseModel):
    car_damage:Optional[str]


class Accident_statement_InDB(IDModelMixin, DateTimeModelMixin, Accident_statement_Base):
    user_id: int
    vehicle_id: int
    accident_id: int
    insurance_id: int
    role_id:int
    car_damage:Optional[str]
    done: bool

class Accident_statement_Public(Accident_statement_InDB):
    vehicle: Optional[VehiclesPublic]
    user: Optional[ProfilePublic]
    role: Optional[RolePublic]
    insurance: Optional[InsurancePublic]
    sketch: Optional[Only_Sketch]
    images: Optional[List[Accident_Image_Public]]


class AccidentImage(BaseModel):
    image: bytes
