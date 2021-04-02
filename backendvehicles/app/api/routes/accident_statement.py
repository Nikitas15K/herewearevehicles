from fastapi import Form, File, UploadFile, APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from app.img import IMG_DIR
import os
import io
# from typing import List
# from starlette.status import (
#     HTTP_200_OK,
#     HTTP_201_CREATED,
#     HTTP_400_BAD_REQUEST,
#     HTTP_401_UNAUTHORIZED,
#     HTTP_404_NOT_FOUND,
#     HTTP_422_UNPROCESSABLE_ENTITY,
# )
from app.models.users import UserPublic, UserInDB, ProfilePublic
from app.models.accidents import AccidentPublic, AccidentCreate
from app.models.accident_statement import Accident_statement_Public, Accident_statement_Create
from app.db.repositories.vehicles import VehiclesRepository
from app.db.repositories.accident import AccidentRepository
from app.db.repositories.accident_statement import AccidentStatementRepository
from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.models.accident_statement import CausedByType

router = APIRouter()

# @router.get("/", name="accident:user")
# async def getuser(

# current_user: UserPublic = Depends(get_current_active_user),
#     )-> UserPublic:

#     return current_user

# @router.get("/other", response_model= ProfilePublic, name="accident:otheruser")
# async def getotheruser( user_id:int,
#     current_user: UserPublic = Depends(get_current_active_user),
#     ) -> ProfilePublic:
#     other_user = get_other_user_by_user_id(user_id = user_id)
#     return other_user

# async def create_new_accident(vehicle_id : int,
#     current_user: UserPublic = Depends(get_current_active_user),
#     vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
#     new_accident: AccidentCreate = Body(..., embed=True),
#     accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository))
#     ) -> AccidentPublic:
#     vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)
#     if not vehicle:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")
#     accident = await accident_repo.create_accident_for_vehicle(new_accident= new_accident, vehicle_id = vehicle_id, id = current_user.id)
#     return accident

@router.post("/")
async def create_new_accident_statement(vehicle_id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    new_accident_stmt: Accident_statement_Create = Body(..., embed=True),
    file: UploadFile = File(...),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)
    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")
    accident_permission = get_temporary_driver_data_for_accident_id(new_accident_stmt['accident_id'], current_user.email)
    if not accident_permission or accident_permission.answered == 'True':
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No permission to edit this accident")       
    contents = await myfile.read()
    accident = await accident_stmt_repo.create_new_accident_statement(new_accident= new_accident, vehicle_id = vehicle_id, id = current_user.id,
     image = contents
     )
    return accident

@router.post("/new")
async def create_new_accident_statement(user_id: int = Form(...),
 accident_id:  int = Form(...),
 vehicle_id:  int = Form(...), 
 caused_by: str = Form(...),
 comments: str = Form(...),
 diagram_sketch: UploadFile = File(...),
 image: UploadFile = File(...),
 current_user: UserPublic = Depends(get_current_active_user),
 vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
 temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
 accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    caused_by_enum = CausedByType[caused_by]

    vehicle = await vehicles_repo.get_vehicle_by_id(id= vehicle_id, user_id = current_user.id)
    if not vehicle:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please select one of your vehicles")

    accident_permission = await temporary_repo.get_temporary_driver_data_for_accident_id(accident_id=accident_id, email=current_user.email)
    if not accident_permission or accident_permission['answered'] == 'True':
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No permission to edit this accident")       
    
    # image.seek(0)
    # diagram_sketch.seek(0)
    contentsImage = await image.read()
    contentsDiagram = await diagram_sketch.read()
    new_accident_statement = Accident_statement_Create(user_id=user_id, accident_id=accident_id, vehicle_id = vehicle_id,
    caused_by = caused_by_enum, comments = comments, diagram_sketch = contentsDiagram, image = contentsImage)
    accident = await accident_stmt_repo.create_new_accident_statement(new_accident_statement = new_accident_statement 
    # accident_id = accident_id, vehicle_id = vehicle_id, id = current_user.id,
    # image = contentsImage, diagram_sketch = contentsDiagram
    )

    return accident

# @router.post("/")
# async def create_accident_statement():
#     return {"filename": file.filename}

# @router.get("/")
# async def main():
#     return FileResponse(os.path.join(IMG_DIR, 'nikitas.jpg'))


@router.get("/image/{id}")
async def get_image_from_accident_stmt(
    id:int, accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> bytes:
    image = await accident_stmt_repo.get_image(id = id)
    # print(image.image)
    # file_like = open(os.path.join(IMG_DIR, 'nikitas.jpg'), mode="rb")
    return StreamingResponse(io.BytesIO(image.image), media_type="image/jpeg")


# async def fake_video_streamer():
#     for i in range(10):
#         yield b"some fake video bytes"


# @app.get("/")
# async def main():
#     return StreamingResponse(fake_video_streamer())