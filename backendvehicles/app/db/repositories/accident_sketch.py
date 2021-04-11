from typing import List
from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.models.accident_statement_sketch import Accident_Sketch_Create, Accident_Sketch_InDB, Only_Sketch, Accident_Sketch_Update
from app.api.dependencies.auth import get_other_user_by_user_id
from databases import Database
import json

CREATE_ACCIDENT_SKETCH_FOR_ACCIDENT_QUERY = """
    INSERT INTO accident_statement_sketch(statement_id, sketch)
    VALUES (:statement_id, :sketch)
    RETURNING id, statement_id, sketch, created_at, updated_at;
"""


GET_SKETCH_BY_STATEMENT_ID_QUERY = """
    SELECT sketch
    FROM accident_statement_sketch
    WHERE statement_id = :statement_id ;
"""

GET_ACCIDENT_SKETCH_BY_STATEMENT_ID_QUERY = """
    SELECT id, statement_id, sketch, created_at, updated_at
    FROM accident_statement_sketch
    WHERE statement_id = :statement_id ;
"""

UPDATE_SKETCH_QUERY="""
    UPDATE accident_statement_sketch
    SET sketch = :sketch
    WHERE statement_id = :statement_id 
    RETURNING id, statement_id, sketch, created_at, updated_at;
    """

class AccidentSketchRepository(BaseRepository):

    async def create_new_accident_sketch(self, *, new_accident_sketch: Accident_Sketch_Create)->Accident_Sketch_InDB:
        query_values = new_accident_sketch.get_dict()
        new_sketch = await self.db.fetch_one(query=CREATE_ACCIDENT_SKETCH_FOR_ACCIDENT_QUERY, values=query_values)
        return Accident_Sketch_InDB(**new_sketch)

    async def get_accident_sketch_by_statement_id(self, *, statement_id: int) ->Only_Sketch:
        sketch = await self.db.fetch_one(query=GET_SKETCH_BY_STATEMENT_ID_QUERY, values={"statement_id": statement_id})
        return Only_Sketch.get_list(sketch['sketch'])

    async def update_accident_sketch_by_statement_id(self, *, statement_id: int, updated_sketch: Accident_Sketch_Update) -> Accident_Sketch_InDB:
        sketch = await self.db.fetch_one(query=GET_ACCIDENT_SKETCH_BY_STATEMENT_ID_QUERY, values={"statement_id": statement_id})
        sketch = Accident_Sketch_InDB(**sketch)
        if not sketch:
            return None          
        sketch_update_params = sketch.copy(update=updated_sketch.get_dict())
        try:
            updated_sketch = await self.db.fetch_one(
                query=UPDATE_SKETCH_QUERY, 
                values= sketch_update_params.dict(exclude={"id","created_at", "updated_at"}),
                )
            return Accident_Sketch_InDB(**updated_sketch)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")