from fastapi import APIRouter
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.insurance import router as insurance_router
from app.api.routes.insurance_company import router as insurance_company_router


router = APIRouter()


router.include_router(vehicles_router, prefix='/vehicles', tags=['vehicles'])
router.include_router(insurance_router, prefix='/insurance', tags=['insurance'])
router.include_router(insurance_company_router, prefix='/insurance_company', tags=['insurance_company'])

