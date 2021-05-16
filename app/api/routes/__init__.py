from fastapi import APIRouter
from app.api.routes.vehicles import router as vehicles_router
# from app.api.routes.insurance import router as insurance_router
from app.api.routes.insurance_company import router as insurance_company_router
from app.api.routes.accident import router as accident_router
# from app.api.routes.accident_statement import router as accident_statement_router
# from app.api.routes.accident_sketch import router as sketch_router
# from app.api.routes.temporary_accident_driver_data import router as temporary_accident_driver_data_router

router = APIRouter()


router.include_router(vehicles_router, prefix='/vehicles', tags=['vehicles'])
# router.include_router(insurance_router, prefix='/insurance', tags=['insurance'])
router.include_router(insurance_company_router, prefix='/insurance_company', tags=['insurance_company'])
router.include_router(accident_router,prefix='/accident', tags=['accident'])
# router.include_router(accident_statement_router,prefix='/accident_statement', tags=['accident_statement'])
# router.include_router(sketch_router, prefix='/sketch', tags=['sketch'])
# router.include_router(temporary_accident_driver_data_router,prefix='/temporary_accident_driver_data', tags=['temporary_accident_driver_data'])