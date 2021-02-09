from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.models.vehicles import VehiclesCreate, VehiclesPublic
from app.db.repositories.vehicles import VehiclesRepository
from app.api.dependencies.database import get_repository

router = APIRouter()

@router.get("/", response_model=List[VehiclesPublic], name="vehicles:get-all-vehicles")
async def get_all_vehicles(
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository))
) -> List[VehiclesPublic]:
    return await vehicles_repo.get_all_vehicles()

@router.post("/", response_model=VehiclesPublic, name="vehicles:create-vehicle", status_code=HTTP_201_CREATED)
async def create_new_vehicle(
    new_vehicle: VehiclesCreate = Body(..., embed=True),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehiclesPublic:
    created_vehicle = await vehicles_repo.create_vehicle(new_vehicle=new_vehicle)
    return created_vehicle

@router.get("/{id}/", response_model=VehiclesPublic, name="vehicles:get-vehicle-by-id")
async def get_vehicle_by_id(id: int, vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)))\
                                        -> VehiclesPublic:
    vehicle = await vehicles_repo.get_vehicle_by_id(id=id)

    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No vehicle found with that id")

    return vehicle