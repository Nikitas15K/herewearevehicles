from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import API_PREFIX
from app.models.users import UserInDB, UserPublic, ProfilePublic
from app.db.repositories.users import UsersRepository
# from pydantic import EmailStr

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"http://localhost:8000/api/users/login/token/")

def get_user_from_token(
    *,
    token: str = Depends(oauth2_scheme),
) -> Optional[UserInDB]:
    try:
        user_repo = UsersRepository()
        user = user_repo.get_current_user(token=token)
    except Exception as e:
        raise e
    return user


def get_current_active_user(current_user: UserInDB = Depends(get_user_from_token)) -> Optional[UserPublic]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not an active user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def get_other_user_by_user_id(*,
    token: str = Depends(oauth2_scheme),
    user_id: int
  ):
    try:
        user_repo = UsersRepository()
        other_user = user_repo.get_other_user(token = token, user_id= user_id)
    except Exception as e:
        raise e
    return other_user
