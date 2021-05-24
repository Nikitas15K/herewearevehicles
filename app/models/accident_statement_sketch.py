from typing import Optional, List
from enum import Enum
import json
from pydantic import BaseModel, validator
from app.models.core import DateTimeModelMixin,IDModelMixin


# class BytesBaseModel(BaseModel):
#     @validator('*')
#     def change_bytea_to_bytes(cls, v, values, config, field):
#         if field.outer_type_ is bytes and v:
#             return str(v).encode()
#         return v


class Coordinates(BaseModel):
    offsetX: int
    offsetY: int

class Accident_Sketch_Base(BaseModel):
    pass

class Accident_Sketch_Create(Accident_Sketch_Base):
    statement_id:int
    sketch: Optional[str] 
    def get_dict(self):
        if self.sketch:
            return {'sketch':  self.sketch[1:-1].replace('"', "'"),
                'statement_id': self.statement_id}
        else:
            return {
                'sketch': None,
                'statement_id': self.statement_id}

class Accident_Sketch_Update(Accident_Sketch_Base):
    sketch: Optional[List[Coordinates]] 
    def get_dict(self):
        if self.sketch:
            return {'sketch':  ",".join([str(item.dict()) for item in self.sketch])}
        else:
            return {
                'sketch': None}


class Accident_Sketch_InDB(IDModelMixin, DateTimeModelMixin, Accident_Sketch_Base):
    statement_id:int
    sketch:Optional[str]
    
class Accident_Sketch_Public(Accident_Sketch_InDB):
    pass

class Only_Sketch(BaseModel):
    sketch:Optional[List[Coordinates]]
    @classmethod
    def get_list(cls, instance: Optional[str]):
        if not instance:
            return cls(sketch=None)
        else:
            new = "["+ instance.replace("'", '"')+"]" 
            new_sketch =json.loads(new)

            return cls(sketch=[Coordinates.parse_obj(item) for item in new_sketch])




