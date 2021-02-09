from typing import List
from pydantic import constr
from app.db.repositories.base import BaseRepository
from app.models.vehicles import VehiclesCreate, VehiclesInDB, VehiclesPublic
from app.models.insurance import InsuranceAdd, InsurancePublic
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
    SELECT id, sign, type, model, manufacture_year, created_at, updated_at
    FROM vehicles
    WHERE sign = :sign;
"""

GET_ALL_VEHICLES_QUERY = """
    SELECT id, sign, type, model, manufacture_year, created_at, updated_at 
    FROM vehicles;  
"""


class VehiclesRepository(BaseRepository):
    """"
    All database actions associated with the Vehicle resource

    """

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.insurance_repo = InsuranceRepository(db)  

    async def get_vehicle_by_id(self, *, id: int) -> VehiclesInDB:
        vehicle = await self.db.fetch_one(query=GET_VEHICLE_BY_ID_QUERY, values={"id": id})
        if not vehicle:
            return None
        return VehiclesInDB(**vehicle)

    async def get_vehicle_by_sign(self, *, sign: str, populate: bool = True) -> VehiclesInDB:
        vehicle_record = await self.db.fetch_one(query=GET_VEHICLE_BY_SIGN_QUERY, values={"sign": sign})

        if vehicle_record:
            vehicle = VehiclesInDB(**vehicle_record)

            if populate:
                return await self.populate_vehicle(vehicle=vehicle)

            return vehicle

    async def get_all_vehicles(self) -> List[VehiclesInDB]:
        vehicles_records = await self.db.fetch_all(query=GET_ALL_VEHICLES_QUERY)
        return [VehiclesInDB(**l) for l in vehicles_records]

    
    async def create_vehicle(self, *, new_vehicle: VehiclesCreate) -> VehiclesInDB:
        query_values = new_vehicle.dict()
        created_vehicle = await self.db.fetch_one(query=CREATE_VEHICLE_QUERY, values=query_values)

        await self.insurance_repo.create_insurance_for_vehicle(insurance_create=InsuranceAdd(vehicle_id=created_vehicle["id"]))
        return await self.populate_vehicle(vehicle=VehiclesInDB(**created_vehicle))


    async def populate_vehicle(self, *, vehicle: VehiclesInDB) -> VehiclesInDB:
        return VehiclesPublic(
            # unpack the vehicle in db instance,
            **vehicle.dict(),
            # fetch the vehicle's insurance from the insurance_repo
            insurance=await self.insurance_repo.get_insurance_by_vehicle_id(vehicle_id=vehicle.id),
        )