from typing import List
import datetime
from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.db.repositories.vehicles import VehiclesRepository
from app.db.repositories.insurance import InsuranceRepository
from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
from app.db.repositories.accident_sketch import AccidentSketchRepository
from app.models.accident_statement import Accident_statement_Create, Accident_statement_InDB, Accident_statement_Public, Accident_statement_Update, AccidentImage
from app.models.accident_statement_sketch import Accident_Sketch_Update, Accident_Sketch_InDB
from app.api.dependencies.auth import get_other_user_by_user_id
from databases import Database
from pydantic import EmailStr


CREATE_FIRST_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY = """
    INSERT INTO accident_statement(user_id, accident_id, vehicle_id, insurance_id, caused_by, comments)
    VALUES (:user_id, :accident_id, :vehicle_id, :insurance_id, 'add cause', 'add comment')
    RETURNING id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at;
"""

GET_ACCIDENT_STATEMENT_BY_ACCIDENT_ID_USER_ID_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
    WHERE accident_id = :accident_id AND user_id= :user_id;
"""

GET_ALL_ACCIDENT_STATEMENTS_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
"""

GET_ACCIDENT_STATEMENT_BY_ACCIDENT_ID_USER_ID_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
    WHERE accident_id = :accident_id AND user_id= :user_id;
"""

GET_ACCIDENT_STATEMENTS_BY_ACCIDENT_ID_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
    WHERE accident_id = :accident_id;
"""

GET_ACCIDENT_IMAGE_BY_ID_QUERY = """
    SELECT image
    FROM accident_statement
    WHERE id = :id;
"""


CREATE_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY = """
    INSERT INTO accident_statement(user_id, accident_id, vehicle_id, insurance_id, caused_by, comments)
    VALUES (:user_id, :accident_id, :vehicle_id, :insurance_id, :caused_by, :comments)
    RETURNING id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at;
"""

UPDATE_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY = """
    UPDATE accident_statement
        SET caused_by = :caused_by, 
            comments = :comments
    WHERE accident_id = :accident_id AND user_id= :user_id
    RETURNING id, user_id, accident_id, vehicle_id, insurance_id, caused_by, comments, created_at, updated_at;
"""

UPDATE_SKETCH_QUERY="""
    UPDATE accident_statement_sketch
    SET sketch = :sketch
    WHERE statement_id = :statement_id 
    RETURNING id, statement_id, sketch, created_at, updated_at;
    """

class AccidentStatementRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.vehicles_repo = VehiclesRepository(db)
        self.insurance_repo = InsuranceRepository(db)
        self.temporary_repo = TemporaryRepository(db)
        self.sketch_repo = AccidentSketchRepository(db)

    async def create_accident_statement(self, *, vehicle_id: int, user_id:int, accident_id:int) -> Accident_statement_InDB:
        vehicle=await self.vehicles_repo.get_vehicle_by_id(id=vehicle_id, user_id= user_id)
        created_accident_statement = await self.db.fetch_one(query=CREATE_FIRST_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY, values={"vehicle_id": vehicle_id, "user_id":user_id, "accident_id":accident_id, "insurance_id":vehicle.insurance.id})
        return created_accident_statement

    async def get_accident_statement_by_accident_id_user_id(self, *,accident_id: int, user_id:int, populate: bool = True):
        accident_statement = await self.db.fetch_one(query=GET_ACCIDENT_STATEMENT_BY_ACCIDENT_ID_USER_ID_QUERY, values={"accident_id": accident_id, "user_id":user_id})
        if not accident_statement:
            return None
        else:
            accident_statement = Accident_statement_InDB(**accident_statement)
            if populate:
                return await self.populate_accident_statement(accident_statement = accident_statement)
        return accident_statement

    async def populate_accident_statement(self, *,
     accident_statement: Accident_statement_InDB
     ) -> Accident_statement_InDB:
        return Accident_statement_Public(
            **accident_statement.dict(),
            vehicle=await self.vehicles_repo.get_vehicle_by_id(id=accident_statement.vehicle_id, user_id= accident_statement.user_id),
            user=get_other_user_by_user_id(user_id = accident_statement.user_id),
            insurance= await self.insurance_repo.get_insurance_by_id(id=accident_statement.insurance_id),
            sketch = await self.sketch_repo.get_accident_sketch_by_statement_id(statement_id=accident_statement.id)        
        )
    
    async def get_all_accident_statements_for_accident_id(self, *, accident_id: int, populate: bool = True)-> List[Accident_statement_InDB]:
        accident_statements = await self.db.fetch_all(query=GET_ACCIDENT_STATEMENTS_BY_ACCIDENT_ID_QUERY, values={"accident_id": accident_id})
        accident_statements_list = []
        for accident_statement in accident_statements:
            accident_statement = Accident_statement_InDB(**accident_statement)
            if populate:
                stmt = await self.populate_accident_statement(accident_statement = accident_statement)
                accident_statements_list.append(stmt)
        return accident_statements_list

    async def create_new_accident_statement(self, *, new_accident_statement: Accident_statement_Create)->Accident_statement_InDB:
        query_values = new_accident_statement.dict(exclude_unset=True)
        new_accident_statement = await self.db.fetch_one(query=CREATE_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY, values=query_values)
        return await self.populate_accident_statement(accident_statement = Accident_statement_InDB(**new_accident_statement))

    # async def get_image(self, *, id: int)->AccidentImage:
    #     image = await self.db.fetch_one(query=GET_ACCIDENT_IMAGE_BY_ID_QUERY, values={'id':id})
    #     return AccidentImage(**image)
        

######################################ftiakse to montelo sto migrate


    async def update_accident_statement(self, *, accident_id: int, user_id:int, accident_statement_update: Accident_statement_Update):
        accident_statement = await self.get_accident_statement_by_accident_id_user_id(accident_id=accident_id, user_id= user_id, populate = False)

        if not accident_statement:
            return None
      
        stmt_update_params = accident_statement.copy(update=accident_statement_update.dict(exclude_unset=True))
        print(stmt_update_params)
        try:
            updated_stmt = await self.db.fetch_one(
                query=UPDATE_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY, 
                values= stmt_update_params.dict(exclude={"id","created_at", "updated_at", "vehicle_id", "insurance_id"}),
                )
            print(updated_stmt)
            return updated_stmt
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")


    async def update_accident_sketch(self, *,accident_id: int, user_id:int, updated_sketch: Accident_Sketch_Update) -> Accident_Sketch_InDB:
        accident_statement = await self.get_accident_statement_by_accident_id_user_id(accident_id=accident_id, user_id= user_id, populate = False)

        if not accident_statement:
            return None
        
        sketch = await self.sketch_repo.get_accident_sketch_by_statement_id(statement_id=accident_statement.id)
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
