from app.db.repositories.base import BaseRepository
from app.models.roles import RoleCreate, RoleInDB, RoleUpdate
from starlette.status import HTTP_400_BAD_REQUEST
from fastapi import HTTPException

CREATE_ROLE_OF_USER_FOR_VEHICLE_QUERY = """
    INSERT INTO roles (role, user_id, vehicle_id)
    VALUES (:role, :user_id, :vehicle_id)
    RETURNING id, role, user_id, vehicle_id, created_at, updated_at;
"""

UPDATE_ROLE_BY_ID_QUERY="""
    UPDATE roles
    SET role = :role
    WHERE vehicle_id = :vehicle_id
    RETURNING id, role, vehicle_id, user_id, created_at, updated_at;
    """

GET_USER_ROLE_BY_VEHICLE_ID_QUERY = """
    SELECT id, role, user_id, vehicle_id, created_at, updated_at
    FROM roles
    WHERE vehicle_id = :vehicle_id;
"""



class RolesRepository(BaseRepository):
    async def create_role_of_user_for_vehicle(self, *, role_create: RoleCreate) -> RoleInDB:
        created_role = await self.db.fetch_one(query=CREATE_ROLE_OF_USER_FOR_VEHICLE_QUERY, values=role_create.dict())
        return created_role

    async def get_user_role_by_vehicle_id(self, *, vehicle_id: int) -> RoleInDB:
        role_record = await self.db.fetch_one(query=GET_USER_ROLE_BY_VEHICLE_ID_QUERY, values={"vehicle_id": vehicle_id})
        if not role_record:
            return None
        return RoleInDB(**role_record)



    async def update_role(self, *, vehicle_id: int, role_update: RoleUpdate) -> RoleInDB:
        role = await self.get_user_role_by_vehicle_id(vehicle_id=vehicle_id)

        if not role:
            return None
       
        role_update_params = role.copy(update=role_update.dict(exclude_unset=True))
        try:
            updated_role = await self.db.fetch_one(
                query=UPDATE_ROLE_BY_ID_QUERY, 
                values= role_update_params.dict(exclude={"id", "user_id", "created_at", "updated_at"}),
                )
            return RoleInDB(**updated_role)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid update params.")