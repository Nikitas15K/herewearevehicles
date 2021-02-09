from pydantic import BaseModel, EmailStr
from app.models.core import DateTimeModelMixin, IDModelMixin
from typing import Optional

class InsuranceCompany(BaseModel):
    """
    ...
    """
    name: Optional[str]
    email: Optional[EmailStr]


class InsuranceCompanyInDB(InsuranceCompany, IDModelMixin):
    name: str
    email: EmailStr


class InsuranceCompanyCreate(InsuranceCompany):
    name: str
    email: EmailStr


class InsuranceCompanyPublic(InsuranceCompany, IDModelMixin):
    pass
