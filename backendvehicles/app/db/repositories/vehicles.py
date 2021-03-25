from typing import List
from app.db.repositories.base import BaseRepository
from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.models.vehicles import VehiclesCreate, VehiclesInDB, VehiclesPublic
from app.models.insurance import InsuranceAdd, InsurancePublic, InsuranceInDB, InsuranceUpdate
from app.db.repositories.insurance import InsuranceRepository
from app.db.repositories.roles import RolesRepository
from app.models.roles import RoleCreate
from app.models.users import UserPublic
from databases import Database

CREATE_VEHICLE_QUERY = """
    INSERT INTO vehicles (sign, type, model, manufacture_year)
    VALUES (UPPER(:sign), :type, UPPER(:model), :manufacture_year)
    ON CONFLICT(sign) DO UPDATE
    SET type=EXCLUDED.type,
        model=EXCLUDED.model,
        manufacture_year=EXCLUDED.manufacture_year  
    RETURNING id, sign, type, model, manufacture_year, created_at, updated_at;

"""

GET_VEHICLE_BY_ID_QUERY = """
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
        r.id AS role_id, r.role, r.user_id, r.vehicle_id
    FROM vehicles v
        INNER JOIN roles r
        ON v.id = r.vehicle_id
    WHERE v.id = :id AND r.user_id = :user_id;

"""

# GET_VEHICLES_BY_USER_ID_QUERY = """
#     SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
#         r.id AS role_id, r.role, r.user_id, r.vehicle_id,
#         r.created_at AS role_create_at, r.updated_at AS role_updated_at
#     FROM vehicles v
#         INNER JOIN roles r
#         ON v.id = r.vehicle_id
#     WHERE r.user_id = :id;
# """

GET_VEHICLES_BY_USER_ID_QUERY_WITH_NEWEST = """
SELECT v1.id, v1.sign, v1.type, v1.model, v1.manufacture_year, v1.created_at, v1.updated_at,
        v1.insurance_id, v1.number, v1.expire_date, v1.damage_coverance, v1.insurance_company_id,
        v1.insurance_create_at, v1.insurance_updated_at, r.role, r.user_id
    FROM roles r
    inner JOIN 
        (SELECT v.id AS id, v.sign AS sign, v.type AS type, v.model AS model,
		 v.manufacture_year AS manufacture_year,v.created_at AS created_at, v.updated_at AS updated_at,
        i.id AS insurance_id, i.number AS number, i.expire_date AS expire_date, i.damage_coverance AS damage_coverance,
		i.insurance_company_id AS insurance_company_id, i.created_at AS insurance_create_at,
		i.updated_at AS insurance_updated_at
        FROM vehicles v
        INNER JOIN
            (SELECT id, number, i2.expire_date AS expire_date, i1.vehicle_id,  damage_coverance, insurance_company_id, created_at, updated_at
            FROM 
            (SELECT id, number, expire_date, vehicle_id, damage_coverance, insurance_company_id, created_at, updated_at
            FROM insurance ORDER BY id) AS i1
           inner join (SELECT vehicle_id,MAX(expire_date) AS expire_date FROM insurance group by vehicle_id) AS i2
			ON i1.expire_date = i2.expire_date AND i1.vehicle_id = i2.vehicle_id)
       		AS i
        ON v.id = i.vehicle_id) 
		AS v1     
    ON v1.id = r.vehicle_id 
    WHERE r.user_id =  :id
    ORDER BY v1.id DESC;
"""

GET_VEHICLE_BY_SIGN_QUERY = """
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
        i.id AS insurance_id, i.number, i.expire_date, i.insurance_company_id, i.damage_coverance,
        i.created_at AS insurance_create_at, i.updated_at AS insurance_updated_at
    FROM vehicles v
        INNER JOIN insurance i
        ON v.id = i.vehicle_id
    WHERE v.id = (SELECT id FROM vehicles WHERE sign = :sign);
"""

GET_ALL_VEHICLES_QUERY = """
    SELECT id, sign, type, model, manufacture_year, created_at, updated_at
    FROM vehicles;
"""

GET_ALL_VEHICLES_QUERY_WITH_NEWEST_INSURANCE = """
SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
        i.id AS insurance_id, i.number, i.expire_date, i.damage_coverance, i.insurance_company_id, 
        i.created_at AS insurance_create_at, i.updated_at AS insurance_updated_at
    FROM vehicles v
INNER JOIN
	(SELECT id, number, i2.expire_date AS expire_date, i1.vehicle_id, i1.damage_coverance, insurance_company_id, created_at, updated_at
		FROM 
	 		(SELECT id, number, expire_date, vehicle_id, damage_coverance, insurance_company_id, created_at, updated_at
				FROM insurance ORDER BY id) AS i1
INNER JOIN 
	 (SELECT vehicle_id,MAX(expire_date) AS expire_date FROM insurance group by vehicle_id) AS i2
			ON i1.expire_date = i2.expire_date AND i1.vehicle_id = i2.vehicle_id)
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
        self.roles_repo = RolesRepository(db)

    async def get_vehicle_by_id(self, *, id: int, user_id:int, populate: bool = True):
        vehicle_record = await self.db.fetch_one(query=GET_VEHICLE_BY_ID_QUERY, values={"id": id, "user_id":user_id})
        if not vehicle_record:
            return None
        else:
            vehicle = VehiclesInDB(**vehicle_record)
            if populate:
                return await self.populate_vehicle(vehicle = vehicle)
        return vehicle

    async def get_all_vehicles_with_newest_insurance(self):
        vehicle_records = await self.db.fetch_all(query=GET_ALL_VEHICLES_QUERY_WITH_NEWEST_INSURANCE)
        return vehicle_records 

    async def get_all_vehicles_by_user_id(self,*, id: int) -> List:
        vehicles_records = await self.db.fetch_all(query=GET_VEHICLES_BY_USER_ID_QUERY_WITH_NEWEST, values = {'id': id})
        return vehicles_records

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

    
    async def create_vehicle(self, *, new_vehicle: VehiclesCreate, id) -> VehiclesInDB:
        query_values = new_vehicle.dict()
        new_vehicle = await self.db.fetch_one(query=CREATE_VEHICLE_QUERY, values=query_values)
        already_added = await self.get_vehicle_by_sign(sign = new_vehicle["sign"])
        if already_added:
            await self.roles_repo.create_role_of_user_for_vehicle(role_create= RoleCreate(vehicle_id=new_vehicle["id"], user_id = id))
            return await self.populate_vehicle(vehicle=VehiclesInDB(**new_vehicle))
        else:
            await self.insurances_repo.create_first_insurance_for_vehicle(vehicle_id=new_vehicle["id"])
            await self.roles_repo.create_role_of_user_for_vehicle(role_create= RoleCreate(vehicle_id=new_vehicle["id"], user_id = id))
            return await self.populate_vehicle(vehicle=VehiclesInDB(**new_vehicle))

   
    async def populate_vehicle(self, *, vehicle: VehiclesInDB) -> VehiclesInDB:
        return VehiclesPublic(
            # unpack the vehicle in db instance,
            **vehicle.dict(),
            # fetch the vehicle's insurance from the insurance_repo
            insurance=await self.insurances_repo.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle.id),
            roles=await self.roles_repo.get_user_role_by_vehicle_id(vehicle_id=vehicle.id),
        )
