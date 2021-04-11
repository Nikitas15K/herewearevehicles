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
    start_date: Optional[date]
    expire_date: Optional[date]
    damage_coverance: bool = False
    insurance_company_id: Optional[int] = Field(..., ge=0)


class InsuranceAdd(InsuranceModel):
    number: str
    start_date: Optional[date]
    expire_date: Optional[date]
    vehicle_id: int
    damage_coverance: bool
    insurance_company_id: int 
    
class InsuranceUpdate(InsuranceModel):
    pass

class InsuranceInDB(IDModelMixin, DateTimeModelMixin, InsuranceModel):
    insurance_company_id: int = Field(..., ge=0)
    vehicle_id: int

class InsurancePublic(InsuranceInDB):
    insurance_company: Optional[InsuranceCompanyPublic]
    pass
