from typing import List
import datetime
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from app.models.accidents import AccidentPublic, AccidentInDB, AccidentCreate
from app.db.repositories.base import BaseRepository
from app.models.accident_statement import Accident_statement_Create
from app.db.repositories.accident_statement import AccidentStatementRepository
from databases import Database

CREATE_ACCIDENT_FOR_VEHICLE_QUERY = """
    INSERT INTO accident (date, city_id, address, injuries, road_problems, closed_case)
    VALUES (:date, :city_id, :address, :injuries, :road_problems, :closed_case)
    RETURNING id, date, city_id, address, injuries, road_problems, closed_case, created_at, updated_at;

"""

GET_ALL_ACCIDENTS_QUERY = """
    SELECT id, date, city_id, address, injuries, road_problems, closed_case, created_at, updated_at
    FROM accident;
"""

GET_ACCIDENT_BY_ID_QUERY = """
    SELECT id, date, city_id, address, injuries, road_problems, closed_case, created_at, updated_at
    FROM accident
    WHERE ID = :id ;
"""


GET_ACCIDENT_BY_ID_WITH_STATEMENT_QUERY = """
    SELECT a.id, a.date, a.city_id, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at,
        acst.id AS accident_statement, acst.user_id, acst.vehicle_id, acst.caused_by, acst.comments
    FROM accident AS a 
        INNER JOIN accident_statement AS acst
        ON a.id = acst.accident_id
    WHERE a.id = :id AND acst.user_id= :user_id ;
"""

GET_ACCIDENTS_BY_USER_ID_QUERY = """
    SELECT a.id, a.date, a.city_id, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at,
        acst.id AS accident_statement, acst.user_id, acst.vehicle_id, acst.caused_by, acst.comments
    FROM accident AS a 
        INNER JOIN accident_statement AS acst
        ON a.id = acst.accident_id
    WHERE acst.user_id= :user_id;
"""



class AccidentRepository(BaseRepository):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.accident_statement_repo = AccidentStatementRepository(db)     

    async def create_accident_for_vehicle(self, *, new_accident: AccidentCreate , vehicle_id: int, id:int) -> AccidentInDB:

        query_values = new_accident.dict(exclude_unset=True)
        new_accident = await self.db.fetch_one(query=CREATE_ACCIDENT_FOR_VEHICLE_QUERY, values=query_values)
        await self.accident_statement_repo.create_accident_statement(
            vehicle_id=vehicle_id, user_id = id, accident_id = new_accident["id"])
        return await self.populate_accident(accident=AccidentInDB(**new_accident), user_id = id)


    async def populate_accident(self, *, accident: AccidentInDB, user_id:int) -> AccidentInDB:
        return AccidentPublic(
            **accident.dict(),
            accident_statement=await self.accident_statement_repo.get_accident_statement_by_accident_id_user_id(accident_id=accident.id, user_id= user_id),
        )

    async def get_all_accidents(self) ->List:
        accident_records = await self.db.fetch_all(query=GET_ALL_ACCIDENTS_QUERY)
        return accident_records 

    async def get_accident_by_id(self, *, id: int):
        accident_record = await self.db.fetch_one(query=GET_ACCIDENT_BY_ID_WITH_STATEMENT_QUERY, values={"id": id})
        if not accident_record:
            return None
        return accident_record

    async def get_accident_with_user_statement_by_id(self, *, id: int, user_id:int, populate: bool = True):
        accident_record = await self.db.fetch_one(query=GET_ACCIDENT_BY_ID_WITH_STATEMENT_QUERY, values={"id": id, "user_id":user_id})
        if not accident_record:
            return None
        else:
            accident = AccidentInDB(**accident_record)
            if populate:
                return await self.populate_accident(accident = accident, user_id = user_id)
        return accident

    async def get_accidents_by_user_id(self, *, user_id:int, populate: bool = True):
        accident_records = await self.db.fetch_all(query=GET_ACCIDENTS_BY_USER_ID_QUERY, values={"user_id":user_id})
        accidents_list = []
        if not accident_records:
            return None
        else:
            for accident_record in accident_records:
                accident = AccidentInDB(**accident_record)
                if populate:
                    accident_populated = await self.populate_accident(accident = accident, user_id = user_id)
                    accidents_list.append(accident_populated)
        return accidents_list




    