from typing import List
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from app.models.vehicles import VehiclesPublic, VehiclesInDB
from app.db.repositories.base import BaseRepository
from app.models.insurance import InsuranceAdd, InsuranceUpdate, InsuranceInDB


CREATE_INSURANCE_FOR_VEHICLE_QUERY = """
     INSERT INTO insurance (number, expire_date, vehicle_id, insurance_company_id)
     VALUES (:number, :expire_date, :vehicle_id, :insurance_company_id)
     RETURNING id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at;
"""

GET_EXPIRE_LAST_INSURANCE_BY_VEHICLE_ID_QUERY = """
    SELECT id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at
    FROM insurance
    WHERE vehicle_id = :vehicle_id
    ORDER BY expire_date DESC
    LIMIT 1;
"""

GET_LAST_CREATED_INSURANCE_BY_VEHICLE_ID_QUERY = """
    SELECT id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at
    FROM insurance
    WHERE vehicle_id = :vehicle_id
    ORDER BY id DESC
    LIMIT 1;
"""

GET_ALL_INSURANCES_QUERY = """
    SELECT id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at 
    FROM insurance;  
"""

UPDATE_INSURANCE_BY_ID_QUERY="""
    UPDATE insurance
    SET number = :number,
        expire_date = :expire_date,
        insurance_company_id = :insurance_company_id
    WHERE vehicle_id = : vehicle_id
    RETURNING id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at;
    """

GET_VEHICLE_BY_INSURANCE_ID="""
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at
    FROM vehicles v 
        INNER JOIN insurance i
        ON v.id = i.vehicle_id
    WHERE i.id = :id;
"""

class InsuranceRepository(BaseRepository):

    async def create_insurance_for_vehicle(self, *, insurance_create: InsuranceAdd) -> InsuranceInDB:
        created_insurance = await self.db.fetch_one(query=CREATE_INSURANCE_FOR_VEHICLE_QUERY, values=insurance_create.dict())
        return created_insurance
 
    async def get_expire_last_insurance_by_vehicle_id(self, *, vehicle_id: int) -> InsuranceInDB:
        insurance_record = await self.db.fetch_one(query=GET_EXPIRE_LAST_INSURANCE_BY_VEHICLE_ID_QUERY, values={"vehicle_id": vehicle_id})
        if not insurance_record:
            return None
        return InsuranceInDB(**insurance_record)

    async def get_last_created_insurance_by_vehicle_id(self, *, vehicle_id: int) -> InsuranceInDB:
        insurance_record = await self.db.fetch_one(query=GET_LAST_CREATED_INSURANCE_BY_VEHICLE_ID_QUERY, values={"vehicle_id": vehicle_id})
        if not insurance_record:
            return None
        return InsuranceInDB(**insurance_record)

    async def add_insurance(self, *, new_insurance: InsuranceAdd) -> InsuranceInDB:
        query_values = new_insurance.dict()
        insurance = await self.db.fetch_one(query=ADD_INSURANCE_QUERY, values=query_values)
        return InsuranceInDB(**insurance)

    async def get_all_insurances(self) -> List[InsuranceInDB]:
        insurances_records = await self.db.fetch_all(query=GET_ALL_INSURANCES_QUERY)
        return [InsuranceInDB(**l) for l in insurances_records]

    async def update_last_created_insurance(self, *, vehicle_id: int, insurance_update: InsuranceUpdate) -> InsuranceInDB:
        insurance = await self.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle_id)
        if not insurance:
            return None
        insurance_update_params = insurance.copy(update=insurance_update.dict(exclude_unset=True))

        try:
            
            updated_insurance = await self.db.fetch_one(
                query=UPDATE_INSURANCE_BY_ID_QUERY, values=insurance_update_params.dict(exclude={"vehicle_id", "created_at", "updated_at"})
            )
            return InsuranceInDB(**updated_insurance)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")


    async def get_vehicle_by_insurance_id(self, *, id=int) -> VehiclesPublic:
        vehicle = await self.db.fetch_one(query=GET_VEHICLE_BY_INSURANCE_ID)
        return vehicle
