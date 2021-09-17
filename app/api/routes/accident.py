from typing import List
import datetime
from pydantic import EmailStr
from fastapi import APIRouter, Body, Depends, HTTPException, Form, File, UploadFile
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from app.models.users import UserPublic, UserInDB, ProfileSearch
from app.models.accidents import AccidentPublic, AccidentCreate
from app.models.accident_statement import Accident_statement_Create, Accident_statement_Public, Accident_statement_Update, Accident_Statement_Detection_Update
from app.models.temporary_accident_driver_data import Temporary_Data_Create, Temporary_Data_InDB, Temporary_Data_Public, Temporary_Data_Update
from app.models.accident_statement_sketch import Accident_Sketch_InDB, Accident_Sketch_Public, Accident_Sketch_Update, Accident_Sketch_Create
from app.db.repositories.vehicles import VehiclesRepository
from app.db.repositories.accident import AccidentRepository
from app.models.accident_image import Accident_Image_Public, Accident_Image_Create
from app.db.repositories.accident_statement import AccidentStatementRepository
from app.db.repositories.accident_sketch import AccidentSketchRepository
from app.db.repositories.accident_image import AccidentImageRepository
from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from fastapi.responses import FileResponse, StreamingResponse
import io, os

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

@router.get("/{id}/", response_model=AccidentPublic, name="accident:get-accident-by-id")
async def get_accident_by_id(id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    accidentstmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)))\
                                        -> AccidentPublic:
    if current_user.is_superuser:
        return await accident_repo.get_accident_by_id(id = id)
    else:
        print("ok")
        accident = await accident_repo.get_accident_from_user_with_statement_id(id=id, user_id = current_user.id)
        accident1 = await accident_repo.get_accident_by_temporary_driver_by_email(id=id, email = current_user.email)
        if not accident:
            if not accident1: 
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
            else:       
                accident = accident1
                return accident
        else:
            return accident

@router.post("/temporary/{accident_id}/",
 response_model=Temporary_Data_Public, 
 name="accident:add-drivers-accident-id")
async def add_other_drivers_by_accident_id(accident_id : int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    accidentstmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    new_temporary: Temporary_Data_Create = Body(..., embed=True),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)))-> Temporary_Data_Public:
    
    accident = await accident_repo.get_accident_from_user_with_statement_id(id = accident_id, user_id = current_user.id, populate = True)
    if not accident:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")

    email_list = []
    accident_statements =  await accidentstmt_repo.get_all_accident_statements_for_accident_id(accident_id=accident_id)
    if not accident_statements:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    else:
        for accident_statement in accident_statements:
            email_list.append(accident_statement.user.email)
    if new_temporary.driver_email in email_list:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Driver is already added")
    stmt_list = []
    for i in range(len(accident.accident_statement)):
        stmt_list.append(accident.accident_statement[i].id)
    accident_statement = await accidentstmt_repo.get_accident_statement_by_accident_id_user_id(accident_id = accident_id, user_id = current_user.id, populate = False)

    if not accident_statement:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not made a statement")       

    if accident_statement.id != min(stmt_list):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You can not add drivers")

    if accident_statement.done:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have declares this accident statement as completed")  

    temporary_driver_data = await temporary_repo.add_driver_to_accident(new_temporary= new_temporary, accident_id = accident.id)
    return temporary_driver_data


@router.get("/", response_model=List[AccidentPublic], name="accident:get-accidents-by-user-id")
async def get_accidents_by_id(
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    ) -> List[AccidentPublic]:
    if current_user.is_master:
        accidents = []
    elif current_user.is_superuser:
        return await accident_repo.get_all_accidents_by_insurance_company(insurance_company_email=current_user.email)
    else:
        accidents = await accident_repo.get_accidents_by_user_id(user_id = current_user.id, email=current_user.email)
        if not accidents:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    return accidents

@router.post("/useraccidents/{user_id}", response_model=List[AccidentPublic], name="accident:master-get-accidents-by-user-id")
async def get_master_accidents_by_id(
    user_id:int,
    searched_user: ProfileSearch = Body(..., embed=True),
    current_user: UserPublic = Depends(get_current_active_user),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    ) -> List[AccidentPublic]:
    print(searched_user)
    if current_user.is_master:
        accidents = await accident_repo.get_accidents_by_user_id_master(user_search = searched_user)
        if not accidents:
            accidents = []
        return accidents
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not access to this accident")


@router.post("/accident_stmt/{accident_id}",name="accident:add-accident-stmt")
async def create_new_accident_statement(
    accident_id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    new_accident_stmt: Accident_statement_Create = Body(..., embed=True),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    accident = await accident_repo.get_accident_by_id(id = accident_id)
    accident_permission = await temporary_repo.get_temporary_driver_data_by_driver_email(accident_id=accident_id, email=current_user.email)    
    print(accident_permission)
    vehicle = await vehicles_repo.get_vehicle_by_user_id_digit(sign = accident_permission['vehicle_sign'], user_id = current_user.id)
    if not vehicle:
        raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="You should add vehicle first."
            )

    new_accident_stmt.vehicle_id = vehicle.id 
    new_accident_stmt.role_id= vehicle.roles.id
    new_accident_stmt.insurance_id = vehicle.insurance.id

    expiredate = datetime.datetime(
        year=vehicle.insurance.expire_date.year, 
        month=vehicle.insurance.expire_date.month,
        day=vehicle.insurance.expire_date.day,
    )

    startdate = datetime.datetime(
        year=vehicle.insurance.start_date.year, 
        month=vehicle.insurance.start_date.month,
        day=vehicle.insurance.start_date.day,
    )
    if expiredate < accident.date or startdate > accident.date:
        raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="You should update insurance information first."
            )
    print(new_accident_stmt)
   
    if accident_permission and accident_permission['answered']:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You already have made statement. You can update it.")       


    accident_stmt = await accident_stmt_repo.create_new_accident_statement(new_accident_statement= new_accident_stmt)
    updated_answer =await temporary_repo.update_answered(accident_id=accident_id, email=current_user.email)
     
    return accident_stmt

@router.put("/accident_stmt/{accident_id}",name="accident:edit-accident-stmt")
async def update_accident_statement(
    accident_id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_statement_update: Accident_statement_Update = Body(..., embed=True),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)

    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please can not update this stmt")

    if accident_stmt.done:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have declared this accident statement as completed")  

    updated_stmt = await accident_stmt_repo.update_accident_statement(accident_id= accident_id, user_id = current_user.id, accident_statement_update = accident_statement_update)
    return updated_stmt

@router.put("/accident_stmt_detection/{accident_id}",name="accident:add-damaged-part-detected")
async def update_accident_statement_detection(
    accident_id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_statement_update: Accident_Statement_Detection_Update = Body(..., embed=True),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_statement_Public:
    
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)

    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You can not update this stmt")

    if accident_stmt.done:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have declared this accident statement as completed")  

    updated_stmt = await accident_stmt_repo.update_accident_statement_detection(accident_id= accident_id, user_id = current_user.id, accident_statement_update = accident_statement_update)
    return updated_stmt


@router.post("/accident_sketch/add/{accident_id}",response_model=Accident_Sketch_Public, name="accident:add-sketch", status_code=HTTP_201_CREATED)
async def create_new_accident_sketch(
    accident_id: int,
    new_accident_sketch: Accident_Sketch_Create = Body(..., embed=True),
    current_user: UserPublic = Depends(get_current_active_user),
    sketch_repo: AccidentSketchRepository = Depends(get_repository(AccidentSketchRepository)),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> Accident_Sketch_Public:
  
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)
    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You can not update this sketch")

    if accident_stmt.done:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have declared this accident statement as completed")  

    new_accident_sketch.statement_id=accident_stmt.id
    created_sketch = await sketch_repo.create_new_accident_sketch(new_accident_sketch=new_accident_sketch, statement_id= accident_stmt.id)
    return created_sketch

@router.post("/removetemporary/{id}", response_model=AccidentPublic, name="accident:remove-driver")
async def remove_accident_driver(
    id: int,
    current_user: UserPublic = Depends(get_current_active_user),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    accident_repo: AccidentRepository = Depends(get_repository(AccidentRepository)),
    accidentstmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ):
    accident = await accident_repo.get_accident_by_temporary_driver_id(id = id, populate = True)
    if not accident:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No accident found")
    else:
        print(accident.id)
    stmt_list = []
    for i in range(len(accident.accident_statement)):
        stmt_list.append(accident.accident_statement[i].id)
    accident_statement = await accidentstmt_repo.get_accident_statement_by_accident_id_user_id(accident_id = accident.id, user_id = current_user.id, populate = False)
    if not accident_statement:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not made a statement")

    if accident_statement.done:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have declared this accident statement as completed")
        
    if accident_statement.id != min(stmt_list):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You can not remove drivers")
    temporary_driver_data = await temporary_repo.delete_temporary_by_id(id = id)
    accident_upd = await accident_repo.get_accident_from_user_with_statement_id(id = accident.id, user_id = current_user.id, populate = True)
    return accident_upd

@router.post("/newImage", name="accident:add-accident-image")
async def create_new_accident_image(
 accident_id:  int = Form(...),
 image: UploadFile = File(...),
 current_user: UserPublic = Depends(get_current_active_user),
 accident_image_repo: AccidentImageRepository = Depends(get_repository(AccidentImageRepository)),
 accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ):

    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)
    if not accident_stmt:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You can not add image")
    print("OK")
    if accident_stmt.done:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You have declared this accident statement as completed")  

    contentsImage = await image.read()
    new_accident_image = Accident_Image_Create(statement_id=accident_stmt.id, image = contentsImage)
    accident_image = await accident_image_repo.add_new_accident_image(new_accident_image = new_accident_image)
    return accident_image

@router.get("/image/{id}", name="accident:get-accident-image")
async def get_image_from_accident_stmt(
    id:int,
    current_user: UserPublic = Depends(get_current_active_user),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    accident_image_repo: AccidentImageRepository = Depends(get_repository(AccidentImageRepository)),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    ) -> bytes:
    image_data = await accident_image_repo.get_statement(id = id)
    print(image_data.statement_id)
    if not image_data.statement_id:
         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not access to this accident")
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_id(id=image_data.statement_id)
    print(accident_stmt)
    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not access to this accident")
    temporary = await temporary_repo.get_all_temporary_driver_data_for_accident_id(accident_id=accident_stmt.accident_id)
    email_list = []
    for temporary_accident_driver in temporary:
        email_list.append(temporary_accident_driver["driver_email"])
    if current_user.is_master or current_user.is_superuser or current_user.id == accident_stmt.user_id or current_user.email in email_list:
        image = await accident_image_repo.get_image(id = id)
    else:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not access to this accident")
    return StreamingResponse(io.BytesIO(image.image), media_type="image/jpeg")

@router.get("/imageList/{accident_id}", name="accident:get-accident-image-list")
async def get_image_count_from_accident_stmt(
    accident_id:int,
    current_user: UserPublic = Depends(get_current_active_user),
    accident_image_repo: AccidentImageRepository = Depends(get_repository(AccidentImageRepository)),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    )->List[int]:
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)
    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have not access to this accident")
    ids = await accident_image_repo.get_image_count(statement_id = accident_stmt.id)
    return ids

@router.put("/complete_statement/{accident_id}", response_model=Accident_statement_Public, name="accident_statement:complete-statement")
async def complete_accident_statement(accident_id:int,
    current_user: UserInDB = Depends(get_current_active_user),
    accident_stmt_repo: AccidentStatementRepository = Depends(get_repository(AccidentStatementRepository)),
    temporary_repo: TemporaryRepository = Depends(get_repository(TemporaryRepository)),
    accident_image_repo: AccidentImageRepository = Depends(get_repository(AccidentImageRepository)),
    sketch_repo: AccidentSketchRepository = Depends(get_repository(AccidentSketchRepository)),
)-> Accident_statement_Public:
    temporary = await temporary_repo.get_all_temporary_driver_data_for_accident_id(accident_id=accident_id)
    if not temporary:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You should add another driver first")
    accident_stmt = await accident_stmt_repo.get_accident_statement_by_accident_id_user_id(accident_id= accident_id, user_id = current_user.id)
    if not accident_stmt:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="You have no access to this accident")
    if accident_stmt.caused_by == 'add cause' or accident_stmt.comments == '' or accident_stmt.comments == 'add comment':
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You have to complete the accident stmt")
    image_count = await accident_image_repo.get_image_count(statement_id = accident_stmt.id)
    email_list = []
    for temporary_accident_driver in temporary:
        email_list.append(temporary_accident_driver["driver_email"])
    if image_count == 0 and current_user.email not in email_list:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You have to add at least one picture")

    stmt_sketch = await sketch_repo.get_accident_sketch_by_statement_id(statement_id = accident_stmt.id)
    if not stmt_sketch:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You have to draw the accident")
    updated_stmt = await accident_stmt_repo.complete_accident_statement(accident_id= accident_id, user_id = current_user.id)
    return updated_stmt
    

    
    
