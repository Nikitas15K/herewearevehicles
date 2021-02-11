from typing import List
from app.db.repositories.base import BaseRepository
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from app.models.vehicles import VehiclesCreate, VehiclesInDB, VehiclesPublic
from app.models.insurance import InsuranceAdd, InsurancePublic, InsuranceInDB, InsuranceUpdate
from app.db.repositories.insurance import InsuranceRepository
from databases import Database


CREATE_VEHICLE_QUERY = """
    INSERT INTO vehicles (sign, type, model, manufacture_year)
    VALUES (:sign, :type, :model, :manufacture_year)
    ON CONFLICT(sign) DO UPDATE
    SET type=EXCLUDED.type,
        model=EXCLUDED.model,
        manufacture_year=EXCLUDED.manufacture_year  
    RETURNING id, sign, type, model, manufacture_year, created_at, updated_at;

"""

GET_VEHICLE_BY_ID_QUERY = """
    SELECT id, sign, type, model, manufacture_year, created_at, updated_at
    FROM vehicles
    WHERE id = :id;
"""

GET_VEHICLE_BY_SIGN_QUERY = """
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
        i.id AS insurance_id, i.number, i.expire_date, i.insurance_company_id,
        i.created_at AS insurance_create_at, i.updated_at AS insurance_updated_at
    FROM vehicles v
        INNER JOIN insurance i
        ON v.id = i.vehicle_id
    WHERE v.id = (SELECT id FROM vehicles WHERE sign = :sign);
"""

GET_ALL_VEHICLES_QUERY = """
    SELECT id, sign, type, model, manufacture_year, created_at, updated_at
    FROM vehicles
"""

UPDATE_INSURANCE_BY_ID_QUERY="""
    UPDATE insurance
    SET number = :number,
        expire_date = :expire_date,
        insurance_company_id = :insurance_company_id
    WHERE vehicle_id = : vehicle_id
    RETURNING id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at;
    """

GET_ALL_VEHICLES_QUERY_WITH_VALID_INSURANCE = """
SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
        i.id AS insurance_id, i.number, i.expire_date, i.insurance_company_id,
        i.created_at AS insurance_create_at, i.updated_at AS insurance_updated_at
    FROM vehicles v
        INNER JOIN
	(SELECT id, number, i2.expire_date AS expire_date, vehicle_id, insurance_company_id, created_at, updated_at
		FROM 
	 	(SELECT id, number, expire_date, vehicle_id, insurance_company_id, created_at, updated_at
			FROM insurance ORDER BY id) AS i1
		JOIN (SELECT MAX(expire_date) AS expire_date FROM insurance group by vehicle_id) i2
			ON i1.expire_date = i2.expire_date)
		AS i
		ON v.id = i.vehicle_id;


"""


class VehiclesRepository(BaseRepository):
    """"
    All database actions associated with the Vehicle resource

    """

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.insurances_repo = InsuranceRepository(db)  

    async def get_vehicle_by_id(self, *, id: int, populate: bool = True):
        vehicle_record = await self.db.fetch_one(query=GET_VEHICLE_BY_ID_QUERY, values={"id": id})
        if not vehicle_record:
            return None
        else:
            vehicle = VehiclesInDB(**vehicle_record)
            if populate:
                return await self.populate_vehicle(vehicle = vehicle)
        return vehicle

    async def get_all_vehicles_with_valid_insurance(self):
        vehicle_records = await self.db.fetch_all(query=GET_ALL_VEHICLES_QUERY_WITH_VALID_INSURANCE)
        return vehicle_records


    async def get_vehicle_by_sign(self, *, sign: str, populate: bool = True) -> VehiclesInDB:
        vehicle_record = await self.db.fetch_one(query=GET_VEHICLE_BY_SIGN_QUERY, values={"sign": sign})

        if not vehicle_record:
            return None
        else:
            vehicle = VehiclesInDB(**vehicle_record)
            if populate:
                return await self.populate_vehicle(vehicle = vehicle)
        return vehicle

    async def get_all_vehicles(self) -> List:
        vehicles_records = await self.db.fetch_all(query=GET_ALL_VEHICLES_QUERY)
        return vehicles_records

    
    async def create_vehicle(self, *, new_vehicle: VehiclesCreate) -> VehiclesInDB:
        query_values = new_vehicle.dict()
        created_vehicle = await self.db.fetch_one(query=CREATE_VEHICLE_QUERY, values=query_values)

        await self.insurances_repo.create_insurance_for_vehicle(insurance_create=InsuranceAdd(vehicle_id=created_vehicle["id"]))
        return await self.populate_vehicle(vehicle=VehiclesInDB(**created_vehicle))


    async def add_insurance_by_vehicle_id(self, *, id:int) -> InsuranceInDB:
        vehicle_record = await self.db.fetch_one(query=GET_VEHICLE_BY_ID_QUERY, values={"id": id})
        if not vehicle_record:
            return None
        else:
            await self.insurances_repo.create_insurance_for_vehicle(insurance_create=InsuranceAdd(vehicle_id=vehicle_record["id"]))
            return await self.populate_vehicle(vehicle=VehiclesInDB(**vehicle_record))

    
    async def populate_vehicle(self, *, vehicle: VehiclesInDB) -> VehiclesInDB:
        return VehiclesPublic(
            # unpack the vehicle in db instance,
            **vehicle.dict(),
            # fetch the vehicle's insurance from the insurance_repo
            insurance=await self.insurances_repo.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle.id),
        )

