# from typing import List
# from app.models.cities import CityPublic, CityInDB
# from app.db.repositories.base import BaseRepository
# from databases import Database
# from pydantic import EmailStr

# GET_ALL_CITIES_QUERY = """
#     SELECT id, city, lat, lng, country
#     FROM city;
# """

# class CityRepository(BaseRepository):

#     async def get_all_cities(self):
#         city_records = await self.db.fetch_all(query=GET_ALL_CITIES_QUERY)
#         return city_records 

