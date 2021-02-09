import pytest

from httpx import AsyncClient
from fastapi import FastAPI

from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from app.models.insurance_company import InsuranceCompanyCreate, InsuranceCompanyInDB

# decorate all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_insurance_company():
    return InsuranceCompanyCreate(
        name="Holy",
        email="hereyousend@here.gr",
    )


class TestInsuranceCompanyRoutes:

    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("insurance-company:create-insurance-company"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

    async def test_invalid_input_raises_error(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("insurance-company:create-insurance-company"), json={})
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateInsuranceCompany:
    async def test_valid_input_creates_insurance_company(
        self, app: FastAPI, client: AsyncClient, new_insurance_company: InsuranceCompanyCreate
    ) -> None:
        res = await client.post(
            app.url_path_for("insurance-company:create-insurance-company"),
            json={"new_insurance_company": new_insurance_company.dict()}
        )
        assert res.status_code == HTTP_201_CREATED
        created_insurance_company = InsuranceCompanyCreate(**res.json())
        assert created_insurance_company == new_insurance_company

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
                (None, 422),
                ({}, 422),
                ({"name": "name_sign"}, 422),
                ({"email": "email@email.com"}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
            self, app: FastAPI, client: AsyncClient, invalid_payload: dict, status_code: int
    ) -> None:
        res = await client.post(
            app.url_path_for("insurance-company:create-insurance-company"), json={"new_insurance_company": invalid_payload}
        )
        assert res.status_code == status_code


class TestGetInsuranceCompany:
    async def test_get_insurance_company_by_id(self, app: FastAPI, client: AsyncClient,
                                               test_insurance_company: InsuranceCompanyInDB) -> None:
        res = await client.get(app.url_path_for("insurance-company:get-insurance-company-by-id",
                                                id=test_insurance_company.id))
        assert res.status_code == HTTP_200_OK
        insurance_company = InsuranceCompanyInDB(**res.json())
        assert insurance_company == test_insurance_company

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
        res = await client.get(app.url_path_for("insurance-company:get-insurance-company-by-id", id=id))
        assert res.status_code == status_code

    async def test_get_all_insurance_companies_returns_valid_response(
            self, app: FastAPI, client: AsyncClient, test_insurance_company: InsuranceCompanyInDB
    ) -> None:
        res = await client.get(app.url_path_for("insurance-companies:get-all-insurance-companies"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
        insurance_companies = [InsuranceCompanyInDB(**l) for l in res.json()]
        assert test_insurance_company in insurance_companies

