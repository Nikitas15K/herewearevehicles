import warnings
import os
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from databases import Database

import alembic
from alembic.config import Config

from app.models.vehicles import VehiclesCreate, VehiclesInDB
from app.db.repositories.vehicles import VehiclesRepository
from app.models.insurance import InsuranceAdd, InsuranceInDB
from app.db.repositories.insurance import InsuranceRepository
from app.models.insurance_company import InsuranceCompanyCreate, InsuranceCompanyInDB
from app.db.repositories.insurance_company import InsuranceCompanyRepository

# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")
# Create a new application for testing

@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from app.api.server import get_application
    return  get_application()
# Grab a reference to our database when needed

@pytest.fixture
def db(app: FastAPI) -> Database:
    return app.state._db
# Make requests in our tests

@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client

@pytest.fixture
async def test_vehicle(db: Database) -> VehiclesInDB:
    vehicle_repo = VehiclesRepository(db)
    new_vehicle = VehiclesCreate(
        sign="JAK-1934",
        type="car",
        model="Porches",
        manufacture_year=2019,
    )
    existing_vehicle = await vehicle_repo.get_vehicle_by_sign(sign=new_vehicle.sign)
    if existing_vehicle:
        return existing_vehicle
    return await vehicle_repo.create_vehicle(new_vehicle=new_vehicle)


@pytest.fixture
async def test_insurance_company(db: Database) -> InsuranceCompanyInDB:
    insurance_company_repo = InsuranceCompanyRepository(db)
    new_insurance_company = InsuranceCompanyCreate(
        name="herewego",
        email="hereyoutest@herewego.gr",
    )
    existing_insurance_company = await insurance_company_repo.get_insurance_company_by_email(email=new_insurance_company.email)
    if existing_insurance_company:
        return existing_insurance_company
    return await insurance_company_repo.create_insurance_company(new_insurance_company=new_insurance_company)
