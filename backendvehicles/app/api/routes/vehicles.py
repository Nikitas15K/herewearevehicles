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
from app.models.insurance import InsurancePublic, InsuranceAdd, InsuranceUpdate
from app.models.users import UserPublic, UserInDB
from app.models.roles import RolePublic, RoleUpdate, RoleCreate
from app.db.repositories.vehicles import VehiclesRepository
from app.db.repositories.insurance import InsuranceRepository
from app.db.repositories.roles import RolesRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()

@router.get("/all", response_model= List[VehiclesPublic], name="vehicles:get-all-vehicles")
async def get_all_vehicles(
        current_user: UserPublic = Depends(get_current_active_user),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository))
) -> List[VehiclesPublic]:
    if current_user.is_superuser:
        return await vehicles_repo.get_all_vehicles()
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No access")


@router.post("/", response_model=VehiclesPublic, name="vehicles:create-vehicle", status_code=HTTP_201_CREATED)
async def create_new_vehicle(
    current_user: UserPublic = Depends(get_current_active_user),
    new_vehicle: VehiclesCreate = Body(..., embed=True),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehiclesPublic:
    created_vehicle = await vehicles_repo.create_vehicle(new_vehicle=new_vehicle, id = current_user.id)
    return created_vehicle

@router.get("/no/{id}/", name="vehicles:get-vehicle-by-id")
async def get_vehicle_by_id(id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    roles_repo: RolesRepository = Depends(get_repository(RolesRepository))):

    vehicle = await vehicles_repo.get_vehicle_by_id(id=id, user_id = current_user.id)
    users_list = []
    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No vehicle found with that id")
    else:
        for i in range(len(vehicle.roles)): 
            users_list.append(vehicle.roles[i].user_id)
    if current_user.id in users_list:
        return vehicle
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Please select one of your vehicles")


@router.get("/", response_model= List, name="vehicles:get-all-vehicles-by-user-id")
async def get_all_vehicles_by_user_id(
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> List:
    return await vehicles_repo.get_all_vehicles_by_user_id(id = current_user.id)
    

@router.put("/{vehicle_id}/insurance", response_model=InsurancePublic, name="insurance:update-insurance-by-vehicle-id")
async def update_insurance_by_vehicle_id(vehicle_id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    insurance_update: InsuranceUpdate = Body(..., embed=True),
    insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository))
    ) -> InsurancePublic:
    vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)

    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")

    insurance = await insurances_repo.update_last_created_insurance(vehicle_id= vehicle_id, insurance_update = insurance_update)
    return insurance

@router.post("/{vehicle_id}/insurance", response_model=InsurancePublic, name="insurance:create-insurance-by-vehicle-id")
async def create_insurance_by_vehicle_id(vehicle_id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    new_insurance: InsuranceAdd = Body(..., embed=True),
    insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository))
    ) -> InsurancePublic:
    vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)

    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")

    insurance = await insurances_repo.create_insurance_for_vehicle(new_insurance= new_insurance, vehicle_id = vehicle_id)
    return insurance


@router.put("/{vehicle_id}/role", response_model=RolePublic, name="role:update-role-by-vehicle-id")
async def update_role_by_vehicle_id(vehicle_id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    role_update: RoleUpdate = Body(..., embed=True),
    roles_repo: RolesRepository = Depends(get_repository(RolesRepository))
    ) -> RolePublic:
    vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)

    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")

    role = await roles_repo.update_role(vehicle_id = vehicle_id, user_id = current_user.id, role_update = role_update)
    return role


# @router.get("/newest/", response_model= List[dict], name="vehicles:get-all-vehicles-with-newest-insurance")
# async def get_all_vehicles_with_newest_insurance(
#         vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository))
# ) -> List[dict]:
#     return await vehicles_repo.get_all_vehicles_with_newest_insurance()


# @router.get("/mod/{sign}/", response_model=VehiclesPublic, name="vehicles:get-vehicle-by-sign")
# async def get_vehicle_by_sign(sign: str, vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)))\
#                                         -> VehiclesPublic:
#     vehicle = await vehicles_repo.get_vehicle_by_sign(sign=sign)

#     if not vehicle:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No vehicle found with that id")

#     return vehicle