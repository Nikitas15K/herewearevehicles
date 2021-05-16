import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from app.models.insurance import InsuranceAdd, InsuranceInDB
from app.db.repositories.insurance import InsuranceRepository
from app.models.vehicles import VehiclesInDB, VehiclesPublic
from databases import Database

# decorate all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_insurance():
    return InsuranceAdd(
        number="JA651914",
        expire_date=2031-12-31,
    )


class TestInsuranceRoutes:

    async def test_routes_exist(self, app: FastAPI, client: AsyncClient,  test_vehicle: VehiclesInDB) -> None:
        # Get insurance by vehicle sign
        res = await client.get(app.url_path_for("insurance:get-insurance-by-vehicle-sign", sign=test_vehicle.sign))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        # Update own insurance
        res = await client.put(app.url_path_for("insurance:update-vehicle-insurance"), json={"insurance_update": {}})
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestAddInsurance:
    async def test_insurance_added_for_vehicle(self, app: FastAPI, client: AsyncClient, db: Database) -> None:
        insurance_repo = InsuranceRepository(db)
        new_vehicle = {"sign": "MER-1905", "type": "car", "model": "Mercedes", "manufacture_year": 2000}
        res = await client.post(app.url_path_for("vehicles:create-vehicle"), json={"new_vehicle": new_vehicle})
        assert res.status_code == status.HTTP_201_CREATED

        created_vehicle = VehiclesPublic(**res.json())
        vehicle_insurance = await insurance_repo.get_newer_insurance_by_vehicle_id(vehicle_id=created_vehicle.id)
        assert vehicle_insurance is not None
        assert isinstance(vehicle_insurance, InsuranceInDB)  


    async def test_valid_input_adds_insurance(
        self, app: FastAPI, client: AsyncClient, new_insurance: InsuranceAdd
    ) -> None:
    
        res = await client.post(
            app.url_path_for("insurance: add-insurance"), json={"new_insurance": new_insurance.dict()}
        )
        assert res.status_code == HTTP_201_CREATED
    
        added_insurance = InsuranceAdd(**res.json())
        assert added_insurance == new_insurance
