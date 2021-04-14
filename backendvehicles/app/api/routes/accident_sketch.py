from fastapi import Form, File, UploadFile, APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.models.accident_statement_sketch import Accident_Sketch_Public, Accident_Sketch_Create, Only_Sketch, Accident_Sketch_Update
from app.models.temporary_accident_driver_data import Temporary_Data_Update
from app.db.repositories.accident_sketch import AccidentSketchRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Accident_Sketch_Public, name="sketch:add-sketch", status_code=HTTP_201_CREATED)
async def add_sketch(

    new_accident_sketch: Accident_Sketch_Create = Body(..., embed=True),
    sketch_repo: AccidentSketchRepository = Depends(get_repository(AccidentSketchRepository)),
) -> Accident_Sketch_Public:
    # print(new_accident_sketch)

    created_sketch = await sketch_repo.create_new_accident_sketch(new_accident_sketch=new_accident_sketch)
    return created_sketch

@router.get("/{statement_id}/", response_model=Only_Sketch, name="sketch:get-sketch-by-id")
async def get_vehicle_by_id(statement_id: int,
    sketch_repo: AccidentSketchRepository = Depends(get_repository(AccidentSketchRepository)),
    ) -> Only_Sketch:

    sketch = await sketch_repo.get_accident_sketch_by_statement_id(statement_id=statement_id)
    if not sketch:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No sketch found")
    else:
        return sketch

@router.put("/{statement_id}/", response_model=Accident_Sketch_Public, name="sketch:update-sketch-by-id")
async def update_sketch_by_statement_id(statement_id : int,
    updated_sketch: Accident_Sketch_Update = Body(..., embed=True),
    sketch_repo: AccidentSketchRepository = Depends(get_repository(AccidentSketchRepository)),
    ) -> Accident_Sketch_Public:
    updated_sketch = await sketch_repo.update_accident_sketch_by_statement_id(statement_id=statement_id, updated_sketch=updated_sketch)
    return updated_sketch