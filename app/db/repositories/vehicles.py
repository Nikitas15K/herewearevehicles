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
from pydantic import EmailStr

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
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at
    FROM vehicles v
        INNER JOIN roles r
        ON v.id = r.vehicle_id
    WHERE v.id = :id AND r.user_id = :user_id;

"""

# GET_VEHICLE_BY_SIGN_QUERY is used to check if the vehicle is already added, check create vehicle
GET_VEHICLE_BY_SIGN_QUERY = """
    SELECT v.id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at,
        i.id AS insurance_id, i.number, i.start_date, i.expire_date, i.insurance_company_id, i.damage_coverance,
        i.created_at AS insurance_create_at, i.updated_at AS insurance_updated_at
    FROM vehicles v
        INNER JOIN insurance i
        ON v.id = i.vehicle_id
    WHERE v.id = (SELECT id FROM vehicles WHERE sign = :sign);
"""

GET_VEHICLES_BY_USER_ID_QUERY_WITH_NEWEST = """
SELECT v1.id, v1.sign, v1.type, v1.model, v1.manufacture_year, v1.created_at, v1.updated_at,
        v1.insurance_id, v1.number, v1.start_date, v1.expire_date, v1.damage_coverance, v1.insurance_company_id,
        v1.insurance_create_at, v1.insurance_updated_at, r.role, r.user_id
    FROM 
        (SELECT id, role, r2.user_id, r1.vehicle_id
            FROM 
            (SELECT id, role, vehicle_id, user_id, created_at, updated_at
                FROM roles ORDER BY id) AS r1
                inner join (SELECT MAX(id) AS last_id ,vehicle_id, user_id FROM roles group by vehicle_id, user_id) AS r2
            ON r1.id = r2.last_id AND r1.vehicle_id = r2.vehicle_id) 
        AS r
    inner JOIN 
        (SELECT v.id AS id, v.sign AS sign, v.type AS type, v.model AS model,
		 v.manufacture_year AS manufacture_year,v.created_at AS created_at, v.updated_at AS updated_at,
        i.id AS insurance_id, i.number AS number, i.start_date AS start_date, i.expire_date AS expire_date, i.damage_coverance AS damage_coverance,
		i.insurance_company_id AS insurance_company_id, i.created_at AS insurance_create_at,
		i.updated_at AS insurance_updated_at
        FROM vehicles v
        INNER JOIN
            (SELECT id, number, i1.start_date AS start_date, i2.expire_date AS expire_date, i1.vehicle_id,  damage_coverance, insurance_company_id, created_at, updated_at
            FROM 
            (SELECT id, number, start_date, expire_date, vehicle_id, damage_coverance, insurance_company_id, created_at, updated_at
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

GET_ALL_VEHICLES_QUERY = """
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
            (SELECT id, number, i1.start_date AS start_date, i2.expire_date AS expire_date, i1.vehicle_id,  damage_coverance, insurance_company_id, created_at, updated_at
            FROM 
            (SELECT id, number, start_date, expire_date, vehicle_id, damage_coverance, insurance_company_id, created_at, updated_at
            FROM insurance ORDER BY id) AS i1
           inner join (SELECT vehicle_id,MAX(expire_date) AS expire_date FROM insurance group by vehicle_id) AS i2
			ON i1.expire_date = i2.expire_date AND i1.vehicle_id = i2.vehicle_id)
       		AS i
        ON v.id = i.vehicle_id) 
		AS v1     
    ON v1.id = r.vehicle_id 
    ORDER BY v1.id DESC;

"""

GET_VEHICLES_BY_INSURANCE_COMPANY_QUERY = """

SELECT v.id AS id, v.sign, v.type, v.model, v.manufacture_year, v.created_at, v.updated_at, i1.insurance_id, i1.number, i1.start_date, i1.expire_date, i1.insurance_company_id, i1.damage_coverance
FROM vehicles AS v 
INNER JOIN 
(SELECT i.vehicle_id,i.id AS insurance_id, i.number, i.start_date, i.expire_date, i.insurance_company_id, i.damage_coverance FROM
(SELECT id, number, start_date, i2.expire_date, i1.vehicle_id, i1.damage_coverance, i1.insurance_company_id, i1.created_at, i1.updated_at
FROM insurance AS i1
inner join (SELECT vehicle_id,MAX(expire_date) AS expire_date FROM insurance group by vehicle_id) AS i2
ON i1.expire_date = i2.expire_date AND i1.vehicle_id = i2.vehicle_id)
AS i 
inner join insurance_company as ic
on i.insurance_company_id=ic.id
where ic.email = :insurance_company_email) as i1
on v.id = i1.vehicle_id

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
                return await self.populate_vehicle(vehicle = vehicle, user_id = user_id)
        return vehicle


    async def get_all_vehicles_by_user_id(self,*, id: int) -> List:
        vehicles_records = await self.db.fetch_all(query=GET_VEHICLES_BY_USER_ID_QUERY_WITH_NEWEST, values = {'id': id})
        return vehicles_records

    async def get_all_vehicles_by_insurance_company(self,*, insurance_company_email:EmailStr) -> List:
        vehicles_records = await self.db.fetch_all(query=GET_VEHICLES_BY_INSURANCE_COMPANY_QUERY, values = {'insurance_company_email': insurance_company_email})
        return vehicles_records

    async def get_all_vehicles(self, *, populate: bool = True) -> List:
        vehicle_records = await self.db.fetch_all(query=GET_ALL_VEHICLES_QUERY)
        return vehicle_records
    
    async def create_vehicle(self, *, new_vehicle: VehiclesCreate, id) -> VehiclesInDB:
        query_values = new_vehicle.dict()
        new_vehicle = await self.db.fetch_one(query=CREATE_VEHICLE_QUERY, values=query_values)
        already_added = await self.get_vehicle_by_sign(sign = new_vehicle["sign"])
        if already_added:
            await self.roles_repo.create_role_of_user_for_vehicle(vehicle_id=new_vehicle["id"], user_id = id)
            return await self.populate_vehicle(vehicle=VehiclesInDB(**new_vehicle), user_id=id)
        else:
            await self.insurances_repo.create_first_insurance_for_vehicle(vehicle_id=new_vehicle["id"])
            await self.roles_repo.create_role_of_user_for_vehicle(vehicle_id=new_vehicle["id"], user_id = id)
            return await self.populate_vehicle(vehicle=VehiclesInDB(**new_vehicle), user_id=id)

   
    async def populate_vehicle(self, *, vehicle: VehiclesInDB, user_id: int) -> VehiclesInDB:
        return VehiclesPublic(
            **vehicle.dict(),
            insurance=await self.insurances_repo.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle.id),
            roles=await self.roles_repo.get_user_role_by_vehicle_user_id(vehicle_id=vehicle.id, user_id=user_id),
        )

    async def get_vehicle_by_sign(self, *, sign: str, populate: bool = False) -> VehiclesInDB:
        vehicle_record = await self.db.fetch_one(query=GET_VEHICLE_BY_SIGN_QUERY, values={"sign": sign})

        if not vehicle_record:
            return None
        else:
            vehicle = VehiclesInDB(**vehicle_record)
        return vehicle

    async def get_vehicle_by_user_id_digit(self, *, sign: str, user_id:int, populate: bool = True):
        sign_digit =int(''.join(filter(str.isdigit, sign)))
        print(sign_digit)
        vehicle = ''
        vehicle_records = await self.get_all_vehicles_by_user_id(id = user_id)
        print(len(vehicle_records))
        for vehicle_record in vehicle_records:
            print(1)
            check = int ( ''.join(filter(str.isdigit, vehicle_record['sign'])))
            if check == sign_digit:
                vehicle = VehiclesInDB(**vehicle_record)
                if populate:
                    return await self.populate_vehicle(vehicle = vehicle, user_id = user_id)
        if vehicle == '':
            return None
        else:
            return vehicle
