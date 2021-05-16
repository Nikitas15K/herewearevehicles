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

DELETE_SKETCH_QUERY ="""
    DELETE FROM accident_statement_sketch
    WHERE statement_id = :statement_id 
"""



class AccidentSketchRepository(BaseRepository):

    async def create_new_accident_sketch(self, *, new_accident_sketch: Accident_Sketch_Create, statement_id:int)->Accident_Sketch_InDB:
        sketch = await self.get_accident_sketch_by_statement_id(statement_id=statement_id)
        if sketch:
            await self.delete_sketch(statement_id=statement_id)
        query_values = new_accident_sketch.get_dict()
        new_sketch = await self.db.fetch_one(query=CREATE_ACCIDENT_SKETCH_FOR_ACCIDENT_QUERY, values=query_values)
        return Accident_Sketch_InDB(**new_sketch)
              
    async def delete_sketch(self, *, statement_id:int):
        await self.db.fetch_one(query=DELETE_SKETCH_QUERY, values={"statement_id": statement_id})
        return (print(f"Sketch for {statement_id} is deleted."))

    # async def create_new_accident_sketch(self, *, new_accident_sketch: Accident_Sketch_Create , accident_id: int, user_id:int) -> InsuranceInDB:
    #     insurance = await self.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle_id)
    #     if insurance.expire_date and insurance.expire_date > datetime.date.today() :
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Wait current insurance expire")
    #     if insurance.number == "ADD INSURANCE":
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Please update empty insurance registry")

    #     query_values = new_insurance.dict(exclude_unset=True)
    #     query_values["vehicle_id"] = vehicle_id
    #     if query_values["expire_date"] and query_values["expire_date"] < datetime.date.today():
    #                     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="This insurance is expired")
    #     if query_values["start_date"] and query_values["expire_date"] and query_values["start_date"]> query_values["expire_date"] :
    #                     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Insurance start date is after expire date")
    #     # raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You can only update selected vehicle.")
    #     created_insurance = await self.db.fetch_one(query=CREATE_INSURANCE_FOR_VEHICLE_QUERY, values=query_values)
    #     return created_insurance


    async def get_accident_sketch_by_statement_id(self, *, statement_id: int) ->Only_Sketch:
        sketch = await self.db.fetch_one(query=GET_SKETCH_BY_STATEMENT_ID_QUERY, values={"statement_id": statement_id})
        if not sketch:
            return None
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

            