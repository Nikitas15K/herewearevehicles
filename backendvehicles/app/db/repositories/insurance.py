from typing import List
import datetime
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from app.models.vehicles import VehiclesPublic, VehiclesInDB
from app.db.repositories.base import BaseRepository
from app.db.repositories.insurance_company import InsuranceCompanyRepository
from app.models.insurance import InsuranceAdd, InsuranceUpdate, InsuranceInDB, InsurancePublic
from databases import Database


CREATE_INSURANCE_FOR_VEHICLE_QUERY = """
     INSERT INTO insurance (number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id)
     VALUES (UPPER(:number), :start_date, :expire_date, :damage_coverance, :vehicle_id, :insurance_company_id)
     RETURNING id, number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at;
"""

CREATE_FIRST_INSURANCE_FOR_VEHICLE_QUERY = """
     INSERT INTO insurance (number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id)
     VALUES ('ADD INSURANCE', '2001-01-01', '2001-01-01', 'False', :vehicle_id, 0)
     RETURNING id, number, start_date, expire_date, vehicle_id, insurance_company_id, created_at, updated_at;
"""

GET_EXPIRE_LAST_INSURANCE_BY_VEHICLE_ID_QUERY = """
    SELECT id, number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at
    FROM insurance
    WHERE vehicle_id = :vehicle_id AND expire_date is not null
    ORDER BY expire_date DESC
    LIMIT 1;
"""

GET_INSURANCE_BY_ID_QUERY = """
    SELECT id, number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at
    FROM insurance
    WHERE id = :id;
"""

GET_LAST_CREATED_INSURANCE_BY_VEHICLE_ID_QUERY = """
    SELECT id, number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at
    FROM insurance
    WHERE vehicle_id = :vehicle_id
    ORDER BY id DESC
    LIMIT 1;
"""

GET_ALL_INSURANCES_QUERY = """
    SELECT id, number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at 
    FROM insurance;  
"""

UPDATE_INSURANCE_BY_VEHICLE_ID_QUERY="""
    UPDATE insurance
    SET number = UPPER(:number),
        start_date = :start_date,
        expire_date = :expire_date,
        damage_coverance = :damage_coverance,
        insurance_company_id = :insurance_company_id
    WHERE vehicle_id = :vehicle_id
    RETURNING id, number, start_date, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at;
    """

UPDATE_INSURANCE_BY_ID_QUERY="""
    UPDATE insurance
    SET number = UPPER(:number),
        start_date = :start_date,
        expire_date = :expire_date,
        damage_coverance = :damage_coverance,
        insurance_company_id = :insurance_company_id
    WHERE id = :id
    RETURNING id, number, expire_date, damage_coverance, vehicle_id, insurance_company_id, created_at, updated_at;
    """

GET_VEHICLE_BY_INSURANCE_ID="""
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at
    FROM vehicles v 
        INNER JOIN insurance i
        ON v.id = i.vehicle_id
    WHERE i.id = :id;
"""

GET_VEHICLE_BY_INSURANCE_ID_QUERY = """
SELECT v1.id, v1.sign, v1.type, v1.model, v1.manufacture_year, v1.created_at, v1.updated_at,
        v1.insurance_id, v1.number, v1.start_date, v1.expire_date, v1.damage_coverance, v1.insurance_company_id,
        v1.insurance_create_at, v1.insurance_updated_at, r.role, r.user_id
    FROM roles r
    inner JOIN 
        (SELECT v.id AS id, v.sign AS sign, v.type AS type, v.model AS model,
		 v.manufacture_year AS manufacture_year,v.created_at AS created_at, v.updated_at AS updated_at,
        i.id AS insurance_id, i.number AS number, i.start_date AS start_date, i.expire_date AS expire_date, i.damage_coverance AS damage_coverance,
		i.insurance_company_id AS insurance_company_id, i.created_at AS insurance_create_at,
		i.updated_at AS insurance_updated_at
        FROM vehicles v
        INNER JOIN
            insurance i
        ON v.id = i.vehicle_id) 
		AS v1     
    ON v1.id = r.vehicle_id 
    WHERE v1.insurance_id = :insurance_id
"""


class InsuranceRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.insurance_co_repo = InsuranceCompanyRepository(db) 

    async def create_insurance_for_vehicle(self, *, new_insurance: InsuranceAdd , vehicle_id: int) -> InsuranceInDB:
        insurance = await self.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle_id)
        if insurance.expire_date and insurance.expire_date > datetime.date.today() :
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Wait current insurance expire")
        if insurance.number == "ADD INSURANCE":
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Please update empty insurance registry")

        query_values = new_insurance.dict(exclude_unset=True)
        query_values["vehicle_id"] = vehicle_id
        if query_values["expire_date"] and query_values["expire_date"] < datetime.date.today():
                        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="This insurance is expired")
        if query_values["start_date"] and query_values["expire_date"] and query_values["start_date"]> query_values["expire_date"] :
                        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Insurance start date is after expire date")
        # raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You can only update selected vehicle.")
        created_insurance = await self.db.fetch_one(query=CREATE_INSURANCE_FOR_VEHICLE_QUERY, values=query_values)
        return created_insurance

    async def create_first_insurance_for_vehicle(self, *, vehicle_id: int) -> InsuranceInDB:
        created_insurance = await self.db.fetch_one(query=CREATE_FIRST_INSURANCE_FOR_VEHICLE_QUERY, values={"vehicle_id": vehicle_id})
        return created_insurance

    async def get_insurance_by_id(self, *, id:int, populate: bool = True) -> InsuranceInDB:
        insurance_record = await self.db.fetch_one(query=GET_INSURANCE_BY_ID_QUERY, values={"id": id})
        if not insurance_record:
            return None
        else:    
            insurance =  InsuranceInDB(**insurance_record)
            if populate:
                return await self.populate_insurance(insurance = insurance)
        return insurance


    async def get_last_created_insurance_by_vehicle_id(self, *, vehicle_id: int, populate: bool = True) -> InsuranceInDB:
        insurance_record = await self.db.fetch_one(query=GET_LAST_CREATED_INSURANCE_BY_VEHICLE_ID_QUERY, values={"vehicle_id": vehicle_id})
        if not insurance_record:
            return None
        else:
            insurance = InsuranceInDB(**insurance_record)
            if populate:
                return await self.populate_insurance(insurance = insurance)
        return insurance

    # async def get_expire_last_insurance_by_vehicle_id(self, *, vehicle_id: int) -> InsuranceInDB:
    #     insurance_record = await self.db.fetch_one(query=GET_EXPIRE_LAST_INSURANCE_BY_VEHICLE_ID_QUERY, values={"vehicle_id": vehicle_id})
    #     if not insurance_record:
    #         return None
    #     return InsuranceInDB(**insurance_record)

    # async def add_insurance(self, *, new_insurance: InsuranceAdd) -> InsuranceInDB:
    #     query_values = new_insurance.dict()
    #     insurance = await self.db.fetch_one(query=ADD_INSURANCE_QUERY, values=query_values)
    #     return InsuranceInDB(**insurance)

    async def get_all_insurances(self) -> List[InsuranceInDB]:
        insurances_records = await self.db.fetch_all(query=GET_ALL_INSURANCES_QUERY)
        return [InsuranceInDB(**l) for l in insurances_records]

    # async def update_insurance_by_id(self, *, id, insurance_update: InsuranceUpdate) -> InsuranceInDB:
    #     insurance = await self.get_insurance_by_id(id=id)
    #     if not insurance:
    #         return None

    #     if insurance.expire_date and insurance.expire_date > datetime.date.today() :
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Wait current insurance expire")
    
    #     insurance_update_params = insurance.copy(update=insurance_update.dict(exclude_unset=True))
    #     if insurance_update_params["expire_date"] and insurance_update_params["expire_date"] < datetime.date.today():
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="This insurance is expired")
    #     if insurance_update_params["start_date"] and insurance_update_params["expire_date"] and insurance_update_params["start_date"]> insurance_update_params["expire_date"] :
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Insurance start date is after expire date")
    #     try:
    #         updated_insurance = await self.db.fetch_one(
    #             query=UPDATE_INSURANCE_BY_ID_QUERY, 
    #             values= insurance_update_params.dict(exclude={"vehicle_id","created_at", "updated_at"}),
    #             )
    #         return InsuranceInDB(**updated_insurance)
    #     except Exception as e:
    #         print(e)
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")

    async def update_last_created_insurance(self, *, vehicle_id:int , insurance_update: InsuranceUpdate) -> InsuranceInDB:
        insurance = await self.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle_id, populate = False)
        
        if not insurance:
            return None

        if insurance.expire_date and insurance.expire_date > datetime.date.today() :
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Wait current insurance expire")
        
        insurance_update_params = insurance.copy(update=insurance_update.dict(exclude_unset=True))
        if insurance_update_params.expire_date and insurance_update_params.expire_date < datetime.date.today():
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="This insurance is expired")
        if insurance_update_params.start_date and insurance_update_params.expire_date and insurance_update_params.start_date> insurance_update_params.expire_date :
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Insurance start date is after expire date")
  
        try:
            updated_insurance = await self.db.fetch_one(
                query=UPDATE_INSURANCE_BY_VEHICLE_ID_QUERY, 
                values= insurance_update_params.dict(exclude={"id","created_at", "updated_at"}),
                )
            return InsuranceInDB(**updated_insurance)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")


    async def get_vehicle_by_insurance_id(self, *, id=int) -> VehiclesPublic:
        vehicle = await self.db.fetch_one(query=GET_VEHICLE_BY_INSURANCE_ID_QUERY)
        return vehicle

    async def populate_insurance(self, *, insurance: InsuranceInDB) -> InsuranceInDB:
        return InsurancePublic(
            # unpack the vehicle in db instance,
            **insurance.dict(),
            # fetch the vehicle's insurance from the insurance_repo
            insurance_company=await self.insurance_co_repo.get_insurance_company_by_id(id=insurance.insurance_company_id)
        )