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
from app.models.users import UserPublic, UserInDB
from app.models.accidents import AccidentPublic, AccidentCreate
from app.models.temporary_accident_driver_data import Temporary_Data_Create, Temporary_Data_InDB, Temporary_Data_Public
from app.db.repositories.vehicles import VehiclesRepository
from app.db.repositories.accident import AccidentRepository
from app.db.repositories.accident_statement import AccidentStatementRepository
from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()


@router.post("/{vehicle_id}/", response_model=AccidentPublic, name="accident:create-accident", status_code=HTTP_201_CREATED)
async def create_new_accident(vehicle_id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    new_accident: AccidentCreate = Body(..., embed=True),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository))
    ) -> AccidentPublic:
    vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)

    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")

    accident = await accident_repo.create_accident_for_vehicle(new_accident= new_accident, vehicle_id = vehicle_id, id = current_user.id)
    return accident

@router.get("/all", response_model= List[dict], name="accident:get-all-accidents")
async def get_all_accidents(
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository))
    ) -> List[dict]:
    if current_user.is_superuser:
        return await accident_repo.get_all_accidents()
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No access")

@router.get("/{id}/", response_model=AccidentPublic, name="accident:get-accident-by-id")
async def get_accident_by_id(id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    accidentstmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)))\
                                        -> AccidentPublic:
    accident = await accident_repo.get_accident_with_user_statement_by_id(id=id, user_id = current_user.id)
    if not accident:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    
    if current_user.id != accident.accident_statement.user_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No access to this accident")
    return accident

@router.post("/{id}/temporary", response_model=Temporary_Data_Public, name="accident:add-drivers-accident-id")
async def add_other_drivers_by_accident_id(id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    new_temporary: Temporary_Data_Create = Body(..., embed=True),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository))
    ) -> Temporary_Data_Public:
    accident = await accident_repo.get_accident_with_user_statement_by_id(id=id, user_id = current_user.id, populate = False)
    if not accident:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please add drivers to the current accident")
    temporary_driver_data = await temporary_repo.add_driver_to_accident(new_temporary= new_temporary, accident_id = accident.id)
    return temporary_driver_data

@router.get("/", response_model=List, name="accident:get-accidents-by-user-id")
async def get_accidents_by_id(
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    ) -> List:
    accidents = await accident_repo.get_accidents_by_user_id(user_id = current_user.id)
    if not accidents:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    return accidents


@router.get("/stmt/{accident_id}/", response_model= List, name="accident_statement:get-accident-statements-by-accident-id")
async def get_accident_stmt_by_id(accident_id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository))
    ) -> List :
 
    accident_statements =  await accident_stmt_repo.get_all_accident_statements_for_accident_id(accident_id=accident_id)
    if not accident_statements:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    else:
        users_list = []
        for accident_statement in accident_statements:
            users_list.append(accident_statement.user_id)
        
    temporary_accident_driver_data =  await temporary_repo.get_all_temporary_driver_data_for_accident_id(accident_id=accident_id)
    if temporary_accident_driver_data :
        drivers_list = []
        for temporary_accident_driver in temporary_accident_driver_data:
            drivers_list.append(temporary_accident_driver["driver_email"])

    if current_user.id in users_list or drivers_list and current_user.email in drivers_list:
        return accident_statements, temporary_accident_driver_data 
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No access")
