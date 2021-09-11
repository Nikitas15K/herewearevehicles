from typing import List
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from app.models.accidents import AccidentPublic, AccidentInDB, AccidentCreate
from app.models.temporary_accident_driver_data import Temporary_Data_InDB
from app.db.repositories.base import BaseRepository
from app.models.accident_statement import Accident_statement_Create
from app.models.users import ProfileSearch
from app.db.repositories.accident_statement import AccidentStatementRepository
from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
from databases import Database
from pydantic import EmailStr

CREATE_ACCIDENT_FOR_VEHICLE_QUERY = """
    INSERT INTO accident (date, city, address, injuries, road_problems, closed_case)
    VALUES (:date, UPPER(:city), UPPER(:address), :injuries, :road_problems, :closed_case)
    RETURNING id, date, city, address, injuries, road_problems, closed_case, created_at, updated_at;

"""

GET_ALL_ACCIDENTS_QUERY = """
    SELECT id, date, city, address, injuries, road_problems, closed_case, created_at, updated_at
    FROM accident;
"""

GET_ACCIDENT_BY_ID_QUERY = """
    SELECT id, date, city, address, injuries, road_problems, closed_case, created_at, updated_at
    FROM accident
    WHERE ID = :id ;
"""

GET_ACCIDENTS_BY_TEMPORARY_DRIVER_EMAIL_QUERY = """
    SELECT a.id AS id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
    FROM accident AS a 
        INNER JOIN temporary_accident_driver_data AS tadd
        ON a.id = tadd.accident_id
    WHERE tadd.driver_email = :driver_email ;
"""



GET_ACCIDENT_BY_TEMPORARY_DRIVER_EMAIL_ACCIDENT_ID_QUERY = """
    SELECT a.id AS id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
    FROM accident AS a 
        INNER JOIN temporary_accident_driver_data AS tadd
        ON a.id = tadd.accident_id
    WHERE a.id = :id AND tadd.driver_email = :email ;
"""

GET_ACCIDENT_BY_TEMPORARY_DRIVER_ID_QUERY = """
    SELECT a.id AS id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
    FROM accident AS a 
        INNER JOIN temporary_accident_driver_data AS tadd
        ON a.id = tadd.accident_id
    WHERE tadd.id = :id;
"""

GET_ACCIDENT_BY_USER_ID_WITH_STATEMENT_QUERY = """
    SELECT a.id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
    FROM accident AS a 
        INNER JOIN accident_statement AS acst
        ON a.id = acst.accident_id
    WHERE a.id = :id AND acst.user_id= :user_id ;
"""

GET_ALL_ACCIDENTS_BY_INSURANCE_COMPANY = """
SELECT a.id AS id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
FROM accident AS a 
INNER JOIN 
(select acs.accident_id from accident_statement as acs
inner join (
select i.id 
from insurance as i inner join insurance_company as ic
on i.insurance_company_id=ic.id
where ic.email = :insurance_company_email) as i1
on acs.insurance_id = i1.id) as acs1
on acs1.accident_id=a.id

union

SELECT a.id AS id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
FROM accident AS a 
INNER JOIN 
(select tadd.accident_id from temporary_accident_driver_data as tadd
where tadd.insurance_email = :insurance_company_email) as tadd1
on a.id = tadd1.accident_id

"""

GET_ACCIDENTS_BY_USER_STMT_ID_QUERY = """
    SELECT a.id AS id, a.date, a.city, a.address, a.injuries, a.road_problems, a.closed_case, a.created_at, a.updated_at
    FROM accident AS a 
        INNER JOIN accident_statement AS acst
        ON a.id = acst.accident_id
    WHERE acst.user_id= :user_id;
"""

UPDATE_CLOSED_CASE_QUERY ="""
    UPDATE accident
    SET closed_case = 'true'
    WHERE id = :id
    RETURNING id, date, city, address, injuries, road_problems, closed_case, created_at, updated_at;
    """


class AccidentRepository(BaseRepository):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.accident_statement_repo = AccidentStatementRepository(db)    
        self.temporary_accident_driver_data_repo = TemporaryRepository(db) 


    async def create_accident_for_vehicle(self, *, new_accident: AccidentCreate , vehicle_id: int, id:int) -> AccidentInDB:

        query_values = new_accident.dict(exclude_unset=True)
        new_accident = await self.db.fetch_one(query=CREATE_ACCIDENT_FOR_VEHICLE_QUERY, values=query_values)
        await self.accident_statement_repo.create_accident_statement(
            vehicle_id=vehicle_id, user_id = id, accident_id = new_accident["id"])
        return await self.populate_accident(accident=AccidentInDB(**new_accident))


    async def populate_accident(self, *, accident: AccidentInDB) -> AccidentInDB:
        return AccidentPublic(
            **accident.dict(),
            accident_statement=await self.accident_statement_repo.get_all_accident_statements_for_accident_id(accident_id=accident.id),
            temporary_accident_drivers=await self.temporary_accident_driver_data_repo.get_all_temporary_driver_data_for_accident_id(accident_id=accident.id),
        )

    async def get_accident_by_id(self, *, id: int, populate: bool = True) -> AccidentInDB:
        accident_record = await self.db.fetch_one(query=GET_ACCIDENT_BY_ID_QUERY, values={"id": id})
        if not accident_record:
            return None
        else:
            accident = AccidentInDB(**accident_record)
            if populate:
                return await self.populate_accident(accident = accident)
        return accident

    async def get_accident_from_user_with_statement_id(self, *, id: int, user_id:int, populate: bool = True) -> AccidentPublic:
        accident_record = await self.db.fetch_one(query=GET_ACCIDENT_BY_USER_ID_WITH_STATEMENT_QUERY, values={"id": id, "user_id":user_id})
        if not accident_record:
            return None
        else:
            accident = AccidentInDB(**accident_record)
            if populate:
                return await self.populate_accident(accident = accident)
        return accident

    async def get_accident_by_temporary_driver_id(self, *, id: int, populate: bool = True) -> AccidentPublic:
        accident_record = await self.db.fetch_one(query=GET_ACCIDENT_BY_TEMPORARY_DRIVER_ID_QUERY, values={"id": id})
        if not accident_record:
            return None
        else:
            accident = AccidentInDB(**accident_record)
            if populate:
                return await self.populate_accident(accident = accident)
        return accident

    
    async def get_accident_by_temporary_driver_by_email(self, *, id: int, email:EmailStr, populate: bool = True) -> AccidentPublic:
        accident_record = await self.db.fetch_one(query=GET_ACCIDENT_BY_TEMPORARY_DRIVER_EMAIL_ACCIDENT_ID_QUERY, values={"id": id, "email":email})
        if not accident_record:
            return None
        else:
            accident = AccidentInDB(**accident_record)
            if populate:
                return await self.populate_accident(accident = accident)
        return accident

    # async def get_all_accidents_by_temporary_driver_email(self, *, driver_email: EmailStr)-> List[Temporary_Data_InDB]:
    #     accidents= await self.db.fetch_all(query=GET_ACCIDENTS_BY_TEMPORARY_DRIVER_EMAIL_QUERY, values={"driver_email": email})
    #     return accidents

    async def get_accidents_by_user_id(self, *, user_id:int, email:EmailStr, populate: bool = True)->List[AccidentPublic]:
        accident_records = await self.db.fetch_all(query=GET_ACCIDENTS_BY_USER_STMT_ID_QUERY, values={"user_id":user_id})
        accidents_declares = await self.db.fetch_all(query=GET_ACCIDENTS_BY_TEMPORARY_DRIVER_EMAIL_QUERY, values={"driver_email": email})
        accidents_list = []
        accident_id_list = []
        if not accident_records and not accidents_declares:
            return None
        else:
            for accident_record in accident_records:
                accident_id_list.append(accident_record["id"])
                accident = AccidentInDB(**accident_record)
                if populate:
                    accident_populated = await self.populate_accident(accident = accident)
                    accidents_list.append(accident_populated)
            for accident_declare in accidents_declares:
                if accident_declare['id'] in accident_id_list:
                    pass
                else:
                    accident = AccidentInDB(**accident_declare)
                    if populate:
                        accident_populated = await self.populate_accident(accident = accident)
                        accidents_list.append(accident_populated)
        return accidents_list

    
    async def get_all_accidents(self,*, populate: bool = True) ->List[AccidentPublic]:
        accident_records = await self.db.fetch_all(query=GET_ALL_ACCIDENTS_QUERY)
        accidents_list = []
        for accident_record in accident_records:
            accident = AccidentInDB(**accident_record)
            if populate:
                accident_populated = await self.populate_accident(accident = accident)
                accidents_list.append(accident_populated)
        return accidents_list 


    async def get_all_accidents_by_insurance_company(self,*, insurance_company_email:EmailStr, populate: bool = True) ->List[AccidentPublic]:
        accident_records = await self.db.fetch_all(query=GET_ALL_ACCIDENTS_BY_INSURANCE_COMPANY, values={"insurance_company_email":insurance_company_email})
        accidents_list = []
        for accident_record in accident_records:
            accident = AccidentInDB(**accident_record)
            if populate:
                accident_populated = await self.populate_accident(accident = accident)
                accidents_list.append(accident_populated)
        return accidents_list 

    async def update_closed_case(self, *, id: int, populate: bool = True)->AccidentPublic:
        accident = await self.get_accident_by_id(id= id)
        if not accident:
            return None  
        else:        
            updated_accident = await self.db.fetch_one(query=UPDATE_CLOSED_CASE_QUERY, values={ "id": id })
            accident_closed = AccidentInDB(**updated_accident)
            if populate:
                accident_populated = await self.populate_accident(accident = accident_closed)
            return accident_populated 

    async def get_accidents_by_user_id_master(self, *, user_search:ProfileSearch, populate: bool = True)->List[AccidentPublic]:
        accident_records = await self.db.fetch_all(query=GET_ACCIDENTS_BY_USER_STMT_ID_QUERY, values={"user_id": user_search.user_id})
        accidents_declares = await self.db.fetch_all(query=GET_ACCIDENTS_BY_TEMPORARY_DRIVER_EMAIL_QUERY, values={"driver_email": user_search.email})
        accidents_list = []
        accident_id_list = []
        if not accident_records and not accidents_declares:
            return None
        else:
            for accident_record in accident_records:
                accident_id_list.append(accident_record["id"])
                accident = AccidentInDB(**accident_record)
                if populate:
                    accident_populated = await self.populate_accident(accident = accident)
                    accidents_list.append(accident_populated)
            for accident_declare in accidents_declares:
                if accident_declare['id'] in accident_id_list:
                    pass
                else:
                    accident = AccidentInDB(**accident_declare)
                    if populate:
                        accident_populated = await self.populate_accident(accident = accident)
                        accidents_list.append(accident_populated)
        return accidents_list



    