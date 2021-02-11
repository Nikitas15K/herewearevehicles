from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from app.models.core import DateTimeModelMixin, IDModelMixin
from app.models.insurance_company import InsuranceCompanyPublic

class InsuranceModel(BaseModel):
    """
    ...
    """
    number: Optional[str]
    expire_date: Optional[date]
    insurance_company_id: Optional[int] = Field(..., ge=0)


class InsuranceAdd(InsuranceModel):
    vehicle_id: int
    insurance_company_id: int = 0
    number = "ADD INSURANCE"
    
class InsuranceUpdate(InsuranceModel):
    pass


class InsuranceInDB(IDModelMixin, DateTimeModelMixin, InsuranceModel):
    insurance_company_id: int = Field(..., ge=0)
    vehicle_id: int

class InsurancePublic(InsuranceInDB):
    pass
