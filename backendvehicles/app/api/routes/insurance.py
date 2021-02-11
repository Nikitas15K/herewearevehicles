from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from app.models.insurance import InsuranceAdd, InsurancePublic, InsuranceUpdate
from app.models.vehicles import VehiclesPublic
from app.db.repositories.insurance import InsuranceRepository
from app.api.dependencies.database import get_repository


router = APIRouter()


@router.get("/", response_model=List[InsurancePublic], name="insurance:get-all-insurances")
async def get_all_insurances(
        insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository))
) -> List[InsurancePublic]:
    return await insurances_repo.get_all_insurances()

@router.get("/last_created/{vehicle_id}/", response_model=InsurancePublic, name="insurance:get-last-created-insurance-by-vehicle-id")
async def get_newer_insurance_by_id(vehicle_id : int = Path(..., ge=1, title="The vehicleID of the insurance to get."),
    insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository)),
    ) -> InsurancePublic:
    try:
        insurance = await insurances_repo.get_last_created_insurance_by_vehicle_id(vehicle_id=vehicle_id)
        return insurance
    except:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No insurance found for that vehicle id")


@router.get("/expire_last/{vehicle_id}/", response_model=InsurancePublic, name="insurance:get-expire-last-insurance-by-vehicle-id")
async def get_expire_last_insurance_by_vehicle_id(vehicle_id : int = Path(..., ge=1, title="The vehicleID of the insurance to get."),
    insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository)),
    ) -> InsurancePublic:
    try:
        newer_insurance = await insurances_repo.get_expire_last_insurance_by_vehicle_id(vehicle_id=vehicle_id)
        return newer_insurance
    except:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No insurance found for that vehicle id")

    

@router.put("/{id}/", response_model=InsurancePublic, name="insurance:update-insurance-by-id")
async def update_insurance_by_id(id : int = Path(..., ge=1, title="The ID of the insurance to update."),
    insurance_update: InsuranceUpdate = Body(..., embed=True),
    insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository)),
    ) -> InsurancePublic:
    insurance = await insurances_repo.update_last_created_insurance(vehicle_id=id, insurance_update = insurance_update)
    return insurance

# @router.get("/vehicleinsurance/{id}/", response_model=VehiclesPublic, name="insurance:get-vehicle-by-insurance-id")
# async def get_vehicle_by_insurance_id(id : int,
#         insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository)),
#         ) ->VehiclesPublic:
#     return await insurances_repo.get_vehicle_by_insurance_id()

# @router.post("/vehicle/{id}/", response_model=InsurancePublic, name="insurance:add-insurance", status_code=HTTP_201_CREATED)
# async def add_insurance( id : int ge=1, title="The ID of the vehicle user adds new insurance."
#     new_insurance: InsuranceAdd = Body(..., embed = True),
#     insurances_repo: InsuranceRepository = Depends(get_repository(InsuranceRepository)),
# ) ->InsurancePublic:
#     created_insurance = await insurances_repo.add_insurance(new_insurance=new_insurance)
#     return created_insurance
