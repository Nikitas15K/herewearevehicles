# from typing import List
# from fastapi import APIRouter, Body, Depends, HTTPException
# from starlette.status import (
#     HTTP_200_OK,
#     HTTP_201_CREATED,
#     HTTP_400_BAD_REQUEST,
#     HTTP_401_UNAUTHORIZED,
#     HTTP_404_NOT_FOUND,
#     HTTP_422_UNPROCESSABLE_ENTITY,
# )
# from app.models.users import UserPublic, UserInDB
# from app.models.accidents import AccidentPublic, AccidentCreate
# from app.db.repositories.vehicles import VehiclesRepository
# from app.db.repositories.accident import AccidentRepository
# from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
# from app.db.repositories.accident_statement import AccidentStatementRepository
# from app.api.dependencies.database import get_repository
# from app.api.dependencies.auth import get_current_active_user

# router = APIRouter()

# @router.get("/{accident_id}/", response_model= List, name="temporary_driver_data:get-driver-data-by-accident-id")
# async def get_temporary_driver_data_for_accident_id(accident_id: int,
#     current_user: UserPublic = Depends(get_current_active_user),
#     temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
#     accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository))
#     ) -> List :
    
#     temporary_accident_drivers =  await temporary_repo.get_all_temporary_driver_data_for_accident_id(accident_id=accident_id)
#     drivers_list = []
#     if temporary_accident_drivers :

#         for temporary_accident_driver in temporary_accident_drivers:
#             drivers_list.append(temporary_accident_driver["driver_email"])

#     accident_statements =  await accident_stmt_repo.get_all_accident_statements_for_accident_id(accident_id=accident_id)
#     users_list = []
#     if not accident_statements:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
#     else:
#         for accident_statement in accident_statements:
#             users_list.append(accident_statement.user_id)

#     if drivers_list and current_user.email in drivers_list or current_user.id in users_list:
#         return temporary_accident_drivers
#     else:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No access")
     