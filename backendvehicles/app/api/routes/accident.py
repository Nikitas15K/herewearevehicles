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
from app.models.accident_statement import Accident_statement_Create, Accident_statement_Public, Accident_statement_Update
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

@router.get("/all", response_model= List[AccidentPublic], name="accident:get-all-accidents")
async def get_all_accidents(
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository))
    ) -> List[AccidentPublic]:
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
    accident = await accident_repo.get_accident_from_user_statement_id(id=id, user_id = current_user.id)
    accident1 = await accident_repo.get_accident_by_temporary_driver_by_email(id=id, email = current_user.email)
    if not accident:
        if not accident1: 
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
        else:
            # if current_user.email == accident.temporary_accident_drivers[0].driver_email:         
            accident = accident1
            return accident
            # else:
            #     raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No access to this accident")
    else:
        # if current_user.id != accident.accident_statement[0].user_id:
        #     raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No access to this accident")
        return accident

@router.post("/{id}/temporary",
 response_model=Temporary_Data_Public, 
 name="accident:add-drivers-accident-id")
async def add_other_drivers_by_accident_id(id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    accidentstmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    new_temporary: Temporary_Data_Create = Body(..., embed=True),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)))-> Temporary_Data_Public:
    

    accident = await accident_repo.get_accident_from_user_statement_id(id=id, user_id = current_user.id, populate = True)
    if not accident:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    stmt_list = []
    for i in range(len(accident.accident_statement)):
        stmt_list.append(accident.accident_statement[i].id)
    accident_statement = await accidentstmt_repo.get_accident_statement_by_accident_id_user_id(accident_id=id, user_id = current_user.id, populate = False)
    if accident_statement.id != min(stmt_list):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You can not add drivers")
    temporary_driver_data = await temporary_repo.add_driver_to_accident(new_temporary= new_temporary, accident_id = accident.id)
    return temporary_driver_data


@router.get("/", response_model=List[AccidentPublic], name="accident:get-accidents-by-user-id")
async def get_accidents_by_id(
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    ) -> List[AccidentPublic]:
    accidents = await accident_repo.get_accidents_by_user_id(user_id = current_user.id, email = current_user.email)
    
    if not accidents:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    return accidents


# @router.get("/stmt/{accident_id}/", response_model= List, name="accident_statement:get-accident-statements-by-accident-id")
# async def get_accident_stmt_by_id(accident_id: int,
#     current_user: UserPublic = Depends(get_current_active_user),
#     temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
#     accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository))
#     ) -> List :
 
#     accident_statements =  await accident_stmt_repo.get_all_accident_statements_for_accident_id(accident_id=accident_id)
#     if not accident_statements:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
#     else:
#         users_list = []
#         for accident_statement in accident_statements:
#             users_list.append(accident_statement.user_id)
        
#     temporary_accident_driver_data =  await temporary_repo.get_all_temporary_driver_data_for_accident_id(accident_id=accident_id)
#     if temporary_accident_driver_data :
#         drivers_list = []
#         for temporary_accident_driver in temporary_accident_driver_data:
#             drivers_list.append(temporary_accident_driver["driver_email"])

#     if current_user.id in users_list or drivers_list and current_user.email in drivers_list:
#         return accident_statements, temporary_accident_driver_data 
#     else:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No access")

@router.post("/{accident_id}/accident_stmt")
async def create_new_accident_statement(
    accident_id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    new_accident_stmt: Accident_statement_Create = Body(..., embed=True),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    

    accident_permission = await temporary_repo.get_temporary_driver_data_for_accident_id(accident_id=accident_id, email=current_user.email)    
    print(accident_permission)
    vehicle = await vehicles_repo.get_vehicle_by_user_id_digit(sign = accident_permission['vehicle_sign'], user_id = current_user.id)



    new_accident_stmt.vehicle_id = vehicle.id 
    new_accident_stmt.insurance_id = vehicle.insurance.id
    print(new_accident_stmt)

   
    if accident_permission and accident_permission['answered']:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No permission to declare accident statement here")       


    accident_stmt = await accident_stmt_repo.create_new_accident_statement(new_accident_statement= new_accident_stmt)
    updated_answer =await temporary_repo.update_answered(accident_id=accident_id, email=current_user.email)
     
    return accident_stmt

@router.put("/{accident_id}/accident_stmt")
async def update_accident_statement(
    accident_id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    accident_statement_update: Accident_statement_Update = Body(..., embed=True),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)

    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please can not update this stmt")

    updated_stmt = await accident_stmt_repo.update_accident_statement(accident_id= accident_id, user_id = current_user.id, accident_statement_update = accident_statement_update)
    return updated_stmt
