from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from starlette.status import HTTP_201_CREATED
from app.models.insurance import InsuranceAdd, InsurancePublic, InsuranceUpdate
from app.db.repositories.insurance import InsuranceRepository
from app.api.dependencies.database import get_repository


router = APIRouter()


@router.get("/{sign}/", response_model=InsurancePublic, name="insurance:get-insurance-by-vehicle-sign")
async def get_insurance_by_sign(
    *, sign:str = Path(..., min_length=3, regex="[a-zA-Z0-9_-]+$"),
) -> InsurancePublic:
    return None

@router.put("/vehicleinsurance/", response_model=InsurancePublic, name="insurance:update-vehicle-insurance")
async def update_vehicle_insurance(insurance_update: InsuranceUpdate = Body(..., embed=True)) -> InsurancePublic:
    return None

@router.get("/", response_model=List[InsurancePublic], name="insurance:get-all-insurances")
async def get_all_insurances(
        insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository))
) -> List[InsurancePublic]:
    return await insurances_repo.get_all_insurances()