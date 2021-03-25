from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from app.models.users import UserPublic, UserInDB
from app.models.accidents import AccidentPublic, AccidentCreate
from app.db.repositories.vehicles import VehiclesRepository
from app.db.repositories.accident import AccidentRepository
from app.db.repositories.accident_statement import AccidentStatementRepository
from app.db.repositories.temporary_accident_driver_data import TemporaryRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()
