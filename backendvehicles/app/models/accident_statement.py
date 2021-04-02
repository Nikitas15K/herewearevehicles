from typing import Optional
from enum import Enum
from pydantic import BaseModel, validator
from app.models.core import DateTimeModelMixin,IDModelMixin
from app.models.vehicles import VehiclesPublic
from app.models.users import ProfilePublic

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
    HitWhenVehicleWhenTurntLeft = "turntleft"
    HitWhenVehicleWhenTurntRight = "turnt right"
    HitWhenVehicleWhenWentBackwards = "went backwards"
    HitWhenVehicleWhenWentWrongdirection = "went wrong direction"
    HitWhenVehicleWhenWasDrivingRightInCrossjunction = "drove on the right in the cross junction"
    HitWhenVehicleWhenIgnoredSign = "ignored sign"
    HitWhenVehicleWhenIgnoredRedLight = "ignored red light"

class Accident_statement_Base(BaseModel):
    caused_by: Optional[CausedByType]
    comments: Optional[str]
    diagram_sketch: Optional[bytes] 
    image: Optional[bytes] 


class Accident_statement_Create(Accident_statement_Base):

    user_id: int
    vehicle_id: int
    accident_id: int

class Accident_statement_Update(Accident_statement_Base):
    pass


class Accident_statement_InDB(IDModelMixin, DateTimeModelMixin, Accident_statement_Base):
    user_id: int
    vehicle_id: int
    accident_id: int
    
class Accident_statement_Public(Accident_statement_InDB):
    vehicle: Optional[VehiclesPublic]
    user: Optional[ProfilePublic]

class AccidentImage(BaseModel):
    image: bytes
