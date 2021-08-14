from typing import Optional
from datetime import date
from app.models.core import DateTimeModelMixin, IDModelMixin
from pydantic import EmailStr, constr, HttpUrl, BaseModel


class ProfileBase(BaseModel):
    """
    Leaving off password and salt from base model
    """
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[constr(regex="^\d{1,3}-\d{1,3}?-\d{1,4}?$")]
    licence_number: Optional[str]
    licence_category: Optional[str]
    licence_expire_date: Optional[date]
    image: Optional[HttpUrl]


class ProfileInDB(IDModelMixin, DateTimeModelMixin, ProfileBase):
    user_id: int
    username: Optional[str]
    email: Optional[EmailStr]


class ProfilePublic(ProfileInDB):
    pass


class UserBase(BaseModel):
    """
    Leaving off password and salt from base model
    """
    email: Optional[EmailStr]
    username: Optional[str]
    email_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False
    is_master:bool = False


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    """
    Add in id, created_at, updated_at, and user's password and salt
    """
    password: constr(min_length=7, max_length=100)
    salt: str


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    access_token: Optional[AccessToken]
    profile: Optional[ProfilePublic]