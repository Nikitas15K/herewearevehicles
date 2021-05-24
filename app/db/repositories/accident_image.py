from fastapi import HTTPException, Depends
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.models.accident_image import Accident_Image_Create, Accident_Image_InDB, AccidentImage
from app.api.dependencies.auth import get_other_user_by_user_id
from databases import Database
import json
from typing import List

GET_ACCIDENT_IMAGE_BY_STATEMENT_ID_QUERY = """
    SELECT image
    FROM accident_statement_image
    WHERE statement_id = :statement_id
    ORDER BY ID DESC LIMIT 1;
"""

ADD_ACCIDENT_IMAGE_QUERY = """
    INSERT INTO accident_statement_image(statement_id, image)
    VALUES (:statement_id, :image)
    RETURNING id, statement_id, created_at, updated_at;
"""

GET_ACCIDENT_IMAGE_COUNT_QUERY = """
    SELECT id
    FROM accident_statement_image
    WHERE statement_id = :statement_id
"""


class AccidentImageRepository(BaseRepository):

    async def add_new_accident_image(self, *, new_accident_image: Accident_Image_Create)->Accident_Image_InDB:
        query_values = new_accident_image.dict()
        new_image = await self.db.fetch_one(query=ADD_ACCIDENT_IMAGE_QUERY, values=query_values)
        return Accident_Image_InDB(**new_image)

    async def get_image(self, *, statement_id: int)->AccidentImage:
        image = await self.db.fetch_one(query=GET_ACCIDENT_IMAGE_BY_STATEMENT_ID_QUERY, values={'statement_id': statement_id})
        return AccidentImage(**image)
    
    async def get_image_count(self, *, statement_id: int)->List[int]:
        ids= await self.db.fetch_all(query=GET_ACCIDENT_IMAGE_COUNT_QUERY, values={'statement_id': statement_id})
        id_list=[]
        for item in ids:
            id_list.append(item['id'])
        return id_list

