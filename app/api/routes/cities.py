# from typing import List
# from fastapi import APIRouter, Body, Depends, HTTPException
# from app.models.cities import CityPublic, CityInDB
# from app.db.repositories.cities import CityRepository
# from app.api.dependencies.database import get_repository


# router = APIRouter()

# @router.get("/", name="cities:get-all-cities")
# async def get_all_cities(
#     city_repo: CityRepository = Depends(get_repository(CityRepository))
#     ):

#     return await city_repo.get_all_cities()
