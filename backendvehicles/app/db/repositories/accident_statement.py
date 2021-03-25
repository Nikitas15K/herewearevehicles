from typing import List
import datetime
from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.db.repositories.vehicles import VehiclesRepository
from app.models.accident_statement import Accident_statement_Create, Accident_statement_InDB, Accident_statement_Public
from databases import Database


CREATE_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY = """
    INSERT INTO accident_statement(user_id, accident_id, vehicle_id, caused_by, comments)
    VALUES (:user_id, :accident_id, :vehicle_id, 'add cause', 'add comment')
    RETURNING id, user_id, accident_id, vehicle_id, caused_by, comments, created_at, updated_at;
"""

GET_ACCIDENT_STATEMENT_BY_ACCIDENT_ID_USER_ID_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
    WHERE accident_id = :accident_id AND user_id= :user_id;
"""

GET_ALL_ACCIDENT_STATEMENTS_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
"""

GET_ACCIDENT_STATEMENTS_BY_ACCIDENT_ID_QUERY = """
    SELECT id, user_id, accident_id, vehicle_id, caused_by, comments, created_at, updated_at
    FROM accident_statement
    WHERE accident_id = :accident_id;
"""

class AccidentStatementRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.vehicles_repo = VehiclesRepository(db)
  
    async def create_accident_statement(self, *, vehicle_id: int, user_id:int, accident_id:int) -> Accident_statement_InDB:
        created_accident_statement = await self.db.fetch_one(query=CREATE_ACCIDENT_STATEMENT_FOR_ACCIDENT_QUERY, values={"vehicle_id": vehicle_id, "user_id":user_id, "accident_id":accident_id})
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
        )
    
    async def get_all_accident_statements_for_accident_id(self, *, accident_id: int, populate: bool = True)-> List:
        accident_statements = await self.db.fetch_all(query=GET_ACCIDENT_STATEMENTS_BY_ACCIDENT_ID_QUERY, values={"accident_id": accident_id})
        accident_statements_list = []
        for accident_statement in accident_statements:
            accident_statement = Accident_statement_InDB(**accident_statement)
            if populate:
                stmt = await self.populate_accident_statement(accident_statement = accident_statement)
                accident_statements_list.append(stmt)
        return accident_statements_list

