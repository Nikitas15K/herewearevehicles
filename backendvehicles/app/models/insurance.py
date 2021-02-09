from typing import Optional
from pydantic import BaseModel, Field, constr, validator
from datetime import datetime, date, timedelta
from app.models.core import DateTimeModelMixin, IDModelMixin
from app.models.insurance_company import InsuranceCompanyPublic

class InsuranceModel(BaseModel):
    """
    ...
    """
    number: Optional[str]
    expire_date: Optional[date]
    insurance_company_id: Optional[int] 


class InsuranceAdd(InsuranceModel):
    vehicle_id: int

    
class InsuranceUpdate(InsuranceModel):
    pass


class InsuranceInDB(IDModelMixin, DateTimeModelMixin, InsuranceModel):
    vehicle_id: int
    sign: Optional[str]


class InsurancePublic(InsuranceInDB):
    pass
