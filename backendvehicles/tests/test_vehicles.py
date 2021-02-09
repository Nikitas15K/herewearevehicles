import pytest

from httpx import AsyncClient
from fastapi import FastAPI

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from app.models.vehicles import VehiclesCreate, VehiclesInDB

# decorate all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_vehicle():
    return VehiclesCreate(
        sign="JAK-1964",
        type="car",
        model="Porches",
        manufacture_year=2019,
    )


class TestVehiclesRoutes:

    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("vehicles:create-vehicle"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

    async def test_invalid_input_raises_error(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("vehicles:create-vehicle"), json={})
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateVehicle:
    async def test_valid_input_creates_vehicles(
        self, app: FastAPI, client: AsyncClient, new_vehicle: VehiclesCreate
    ) -> None:
        res = await client.post(
            app.url_path_for("vehicles:create-vehicle"), json={"new_vehicle": new_vehicle.dict()}
        )
        assert res.status_code == HTTP_201_CREATED
        created_vehicle = VehiclesCreate(**res.json())
        assert created_vehicle == new_vehicle

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (

                ({"sign": "te"}, 422),
                ({"sign": "te", "model": "BMW"}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
            self, app: FastAPI, client: AsyncClient, invalid_payload: dict, status_code: int
    ) -> None:
        res = await client.post(
            app.url_path_for("vehicles:create-vehicle"), json={"new_vehicle": invalid_payload}
        )
        assert res.status_code == status_code


class TestGetVehicle:
    async def test_get_vehicle_by_id(self, app: FastAPI, client: AsyncClient, test_vehicle: VehiclesInDB) -> None:
        res = await client.get(app.url_path_for("vehicles:get-vehicle-by-id", id=test_vehicle.id))
        assert res.status_code == HTTP_200_OK
        vehicle = VehiclesInDB(**res.json())
        assert vehicle == test_vehicle

    @pytest.mark.parametrize(
        "id, status_code",
        (
                (500, 404),
                (-1, 404),
                (None, 422),
        ),
    )
    async def test_wrong_id_returns_error(
            self, app: FastAPI, client: AsyncClient, id: int, status_code: int
    ) -> None:
        res = await client.get(app.url_path_for("vehicles:get-vehicle-by-id", id=id))
        assert res.status_code == status_code

    async def test_get_all_vehicles_returns_valid_response(
        self, app: FastAPI, client: AsyncClient, test_vehicle: VehiclesInDB
    ) -> None:
        res = await client.get(app.url_path_for("vehicles:get-all-vehicles"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
        vehicles = [VehiclesInDB(**l) for l in res.json()]
        assert test_vehicle in vehicles

