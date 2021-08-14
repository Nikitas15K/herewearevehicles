from typing import List
from app.models.insurance_company import InsuranceCompanyPublic, InsuranceCompanyCreate
from fastapi import APIRouter, Body, Depends, HTTPException
from app.db.repositories.insurance_company import InsuranceCompanyRepository
from app.api.dependencies.database import get_repository
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.models.users import UserPublic
from app.api.dependencies.auth import get_current_active_user
router = APIRouter()

@router.get("/", name="insurance-companies:get-all-insurance-companies")
async def get_all_insurance_companies(
        insurance_company_repo: InsuranceCompanyRepository = Depends(get_repository(InsuranceCompanyRepository))
):
    return await insurance_company_repo.get_all_insurance_companies()


@router.post("/", response_model=InsuranceCompanyPublic, name="insurance-company:create-insurance-company", status_code=HTTP_201_CREATED)
async def create_new_insurance_company(
    current_user: UserPublic = Depends(get_current_active_user),
    new_insurance_company: InsuranceCompanyCreate = Body(..., embed=True),
    insurance_company_repo: InsuranceCompanyRepository = Depends(get_repository(InsuranceCompanyRepository)),
) -> InsuranceCompanyPublic:
    if current_user.is_master:
        created_insurance_company = await insurance_company_repo.create_insurance_company(new_insurance_company=new_insurance_company)
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No access")
    return created_insurance_company

@router.get("/searchby/{id}/", response_model=InsuranceCompanyPublic, name="insurance-company:get-insurance-company-by-id")
async def get_insurance_company_by_id(id: int, insurance_company_repo: InsuranceCompanyRepository = Depends(get_repository(InsuranceCompanyRepository)))\
                                        -> InsuranceCompanyPublic:
    insurance_company = await insurance_company_repo.get_insurance_company_by_id(id=id)

    if not insurance_company:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No insurance company found with that id")

    return insurance_company

@router.get("/findby/{name}/", response_model=InsuranceCompanyPublic, name="insurance-company:get-insurance-company-by-name")
async def get_insurance_company_by_name(name: str, insurance_company_repo: InsuranceCompanyRepository = 
                                        Depends(get_repository(InsuranceCompanyRepository)))-> InsuranceCompanyPublic:
    insurance_company = await insurance_company_repo.get_insurance_company_by_name(name=name)

    if not insurance_company:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No insurance company found with that name")     

    return insurance_company                               




