from typing import List
from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.models.temporary_accident_driver_data import Temporary_Data_Create, Temporary_Data_InDB, Temporary_Data_Public
from databases import Database
from pydantic import EmailStr

CREATE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY = """
     INSERT INTO temporary_accident_driver_data (accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered)
     VALUES (:accident_id, UPPER(:driver_full_name), :driver_email, UPPER(:vehicle_sign), UPPER(:insurance_number), :insurance_email, :answered)
     RETURNING id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at;
"""

DELETE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY = """
    DELETE FROM temporary_accident_driver_data
    WHERE driver_email = :driver_email
    RETURNING driver_email;
"""

GET_TEMPORARY_DRIVERS_DATA_BY_ACCIDENT_ID_QUERY = """
    SELECT id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at
    FROM temporary_accident_driver_data
    WHERE accident_id = :accident_id;
"""

GET_TEMPORARY_DRIVER_DATA_BY_EMAIL_ACCIDENT_ID_QUERY = """
    SELECT id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at
    FROM temporary_accident_driver_data
    WHERE accident_id = :accident_id AND driver_email = :email;
"""



class TemporaryRepository(BaseRepository):
    async def add_driver_to_accident(self, *, new_temporary: Temporary_Data_Create, accident_id: int) -> Temporary_Data_InDB:
        query_values = new_temporary.dict(exclude_unset=True)
        query_values["accident_id"] = accident_id
        created_temporary = await self.db.fetch_one(query=CREATE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY, values=query_values)
        return created_temporary

    async def delete_cleaning_by_id(self, *, driver_email : EmailStr) -> str:
        return await self.db.execute(query=DELETE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY, values={"driver_email": driver_email})

    async def get_all_temporary_driver_data_for_accident_id(self, *, accident_id: int)-> List[Temporary_Data_InDB]:
        temporary_accident_drivers_data = await self.db.fetch_all(query=GET_TEMPORARY_DRIVERS_DATA_BY_ACCIDENT_ID_QUERY, values={"accident_id": accident_id})
        return temporary_accident_drivers_data

    async def get_temporary_driver_data_for_accident_id(self, *, accident_id: int, email : EmailStr)-> Temporary_Data_InDB:
        temporary_accident_driver_data = await self.db.fetch_one(query=GET_TEMPORARY_DRIVER_DATA_BY_EMAIL_ACCIDENT_ID_QUERY, values={"accident_id": accident_id, "email": email})
        if not temporary_accident_driver_data:
            return None
        return temporary_accident_driver_data

