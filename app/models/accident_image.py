from typing import Optional, List
from enum import Enum
import json
from pydantic import BaseModel, validator
from app.models.core import DateTimeModelMixin,IDModelMixin

class AccidentImage(BaseModel):
    image: Optional[bytes] 

class Accident_Image_Create(AccidentImage):
    statement_id:int
    image: Optional[bytes] 

class Accident_Image_InDB(IDModelMixin, DateTimeModelMixin, AccidentImage):
    statement_id:int
    image: Optional[bytes] 
    
class Accident_Image_Public(Accident_Image_InDB):
    pass
