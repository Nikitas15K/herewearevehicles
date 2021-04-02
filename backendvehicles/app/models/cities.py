        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("city", sa.Text, nullable=False),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lng", sa.Float, nullable=False),
        sa.Column("country", sa.Text, nullable=False),

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from app.models.core import DateTimeModelMixin, IDModelMixin
from app.models.insurance_company import InsuranceCompanyPublic

class CityModel(BaseModel):
    """
    ...
    """
    city: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    country: Optional[str]


class CityAdd(CityModel):
    city: str
    lat: float
    lng: float
    country: str
    
class CityUpdate(CityModel):
    pass

class CityInDB(IDModelMixin, DateTimeModelMixin, CityModel):
    pass

class CityPublic(CityInDB):
    pass