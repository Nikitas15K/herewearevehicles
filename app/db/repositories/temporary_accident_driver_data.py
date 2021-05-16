from typing import List
from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.models.temporary_accident_driver_data import Temporary_Data_Create, Temporary_Data_InDB, Temporary_Data_Public, Temporary_Data_Update
from databases import Database
from pydantic import EmailStr

CREATE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY = """
     INSERT INTO temporary_accident_driver_data (accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered)
     VALUES (:accident_id, UPPER(:driver_full_name), :driver_email, UPPER(:vehicle_sign), UPPER(:insurance_number), :insurance_email, :answered)
     RETURNING id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at;
"""

DELETE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY = """
    DELETE FROM temporary_accident_driver_data
    WHERE id = :id;
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

GET_TEMPORARY_DRIVER_DATA_BY_VEHICLE_ACCIDENT_ID_QUERY = """
    SELECT id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at
    FROM temporary_accident_driver_data
    WHERE accident_id = :accident_id AND vehicle_sign = :vehicle_sign;
"""

UPDATE_ANSWERED_QUERY="""
    UPDATE temporary_accident_driver_data
    SET answered = 'true'
    WHERE accident_id = :accident_id AND driver_email = :email
    RETURNING id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at;
    """

UPDATE_TEMPORARY_QUERY="""
    UPDATE temporary_accident_driver_data
    SET driver_full_name = :driver_full_name, 
            driver_email = :driver_email,
            vehicle_sign = :vehicle_sign, 
            insurance_number = :insurance_number,
            insurance_email = :insurance_email
    WHERE id = :id
    RETURNING id, accident_id, driver_full_name, driver_email, vehicle_sign, insurance_number, insurance_email, answered, created_at, updated_at;
    """



class TemporaryRepository(BaseRepository):
    async def add_driver_to_accident(self, *, new_temporary: Temporary_Data_Create, accident_id: int) -> Temporary_Data_InDB:
        query_values = new_temporary.dict(exclude_unset=True)
        query_values["accident_id"] = accident_id

        driver = await self.get_temporary_driver_data_by_driver_email(accident_id=accident_id, email = query_values["driver_email"] )
        vehicle = await self.get_temporary_driver_data_by_vehicle_sign(accident_id=accident_id, vehicle_sign = query_values["vehicle_sign"] )
        
        if driver and driver["answered"] or vehicle and vehicle["answered"]:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Driver has already made statement for the accident.")
        
        if driver:    
            await self.delete_temporary_by_id(id = driver["id"])
        if vehicle:
            await self.delete_temporary_by_id(id = vehicle["id"])
        created_temporary = await self.db.fetch_one(query=CREATE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY, values=query_values)
        return created_temporary

    async def delete_temporary_by_id(self, *, id : int) -> str:
        return await self.db.execute(query=DELETE_TEMPORARY_DRIVER_FOR_ACCIDENT_QUERY, values={"id": id})

    async def get_all_temporary_driver_data_for_accident_id(self, *, accident_id: int)-> List[Temporary_Data_InDB]:
        temporary_accident_drivers_data = await self.db.fetch_all(query=GET_TEMPORARY_DRIVERS_DATA_BY_ACCIDENT_ID_QUERY, values={"accident_id": accident_id})
        return temporary_accident_drivers_data

    async def get_temporary_driver_data_by_driver_email(self, *, accident_id: int, email : EmailStr)-> Temporary_Data_InDB:
        temporary_accident_driver_data = await self.db.fetch_one(query=GET_TEMPORARY_DRIVER_DATA_BY_EMAIL_ACCIDENT_ID_QUERY, values={"accident_id": accident_id, "email": email})
        if not temporary_accident_driver_data:
            return None
        return temporary_accident_driver_data

    async def get_temporary_driver_data_by_vehicle_sign(self, *, accident_id: int, vehicle_sign : str)-> Temporary_Data_InDB:
        temporary_accident_driver_data = await self.db.fetch_one(query=GET_TEMPORARY_DRIVER_DATA_BY_VEHICLE_ACCIDENT_ID_QUERY,
                                         values={"accident_id": accident_id, "vehicle_sign": vehicle_sign})
        if not temporary_accident_driver_data:
            return None
        return temporary_accident_driver_data

    async def update_answered(self, *, accident_id: int, email : EmailStr)->Temporary_Data_InDB:
        temporary_accident_driver_data = await self.get_temporary_driver_data_by_driver_email(accident_id= accident_id, email= email)

        if not temporary_accident_driver_data:
            return None          
        updated_temporary = await self.db.fetch_one(query=UPDATE_ANSWERED_QUERY, values={"accident_id": accident_id, "email" : email })
        return Temporary_Data_InDB(**updated_temporary)

        # except Exception as e:
        #     print(e)
        #     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")

    # async def update_temporary(self, *, id: int, email : EmailStr, temporary_accident_driver_data_update : Temporary_Data_Update)->Temporary_Data_InDB:
    #     temporary_accident_driver_data = await self.get_temporary_driver_data_by_driver_email(accident_id= accident_id, email= email)
    #     print(temporary_accident_driver_data)
    #     if not temporary_accident_driver_data:
    #         return None          
    #     temporary_update_params = temporary_accident_driver_data.copy(update=temporary_accident_driver_data_update.dict(exclude_unset=True))
    #     print(temporary_update_params)
    #     try:
    #         updated_temp = await self.db.fetch_one(
    #             query=UPDATE_TEMPORARY_QUERY, 
    #             values= temporary_update_params.dict(exclude={"id","created_at", "updated_at", "answered"}),
    #             )
    #         print(updated_temp)
    #         return updated_temp
    #     except Exception as e:
    #         print(e)
    #         raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")
