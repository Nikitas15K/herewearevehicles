from typing import Optional
from enum import Enum
from pydantic import BaseModel
from app.models.core import DateTimeModelMixin,IDModelMixin
from app.models.vehicles import VehiclesPublic

class CausedByType(str, Enum):
    AddCause="add cause"
    Parked = "was parked"
    ExitingParking = "was exiting parking spot"
    EnteringParking = "was entering parking spot"
    Parking = "while was parking"
    DoorOpen = "had door open"
    EnteringTrafficCircle = "was entering traffic circle"
    DrivinTrafficCircle = "was driving traffic circle"
    SameDirectionSameLane = "rear-end vehicle accident while was driving in the same lane"
    SameDirectionDifferentLane = "accident while was driving in the different lane"
    ChangedLane = "changed lane"
    Overtook = "overtook"
    TurntLeft = "turntleft"
    TurntRight = "turnt right"
    Backwards = "went backwards"
    Wrongdirection = "went wrong direction"
    RightInCrossjunction = "drove on the right in the cross junction"
    IgnoredSign = "ignored sign"
    IgnoredRedLight = "ignored red light"

class Accident_statement_Base(BaseModel):
    caused_by: Optional[CausedByType]
    comments: Optional[str]

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