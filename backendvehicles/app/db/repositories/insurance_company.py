from typing import List
from pydantic import EmailStr
from app.db.repositories.base import BaseRepository
from app.models.insurance_company import InsuranceCompanyInDB, InsuranceCompanyCreate

CREATE_INSURANCE_COMPANY_QUERY = """
    INSERT INTO insurance_company (name, email)
    VALUES (:name, :email)
    RETURNING id, name, email, created_at, updated_at;
"""

GET_INSURANCE_COMPANY_BY_ID_QUERY = """
    SELECT id, name, email, created_at, updated_at
    FROM insurance_company
    WHERE id = :id;
"""

GET_INSURANCE_COMPANY_BY_EMAIL_QUERY = """
    SELECT id, name, email, created_at, updated_at
    FROM insurance_company
    WHERE email = :email;
"""


GET_ALL_INSURANCE_COMPANIES_QUERY = """
    SELECT id, name, email, created_at, updated_at
    FROM insurance_company;  
"""


class InsuranceCompanyRepository(BaseRepository):

    async def create_insurance_company(self, *, new_insurance_company: InsuranceCompanyCreate) -> InsuranceCompanyInDB:
        query_values = new_insurance_company.dict()
        insurance_company = await self.db.fetch_one(CREATE_INSURANCE_COMPANY_QUERY, query_values)

        return InsuranceCompanyInDB(**insurance_company)

    async def get_insurance_company_by_id(self, *, id: int) -> InsuranceCompanyInDB:
        insurance_company = await self.db.fetch_one(query=GET_INSURANCE_COMPANY_BY_ID_QUERY, values={"id": id})
        if not insurance_company:
            return None
        return InsuranceCompanyInDB(**insurance_company)

    async def get_insurance_company_by_email(self, *, email: EmailStr) -> InsuranceCompanyInDB:
        insurance_company = await self.db.fetch_one(query=GET_INSURANCE_COMPANY_BY_EMAIL_QUERY, values={"email": email})
        if not insurance_company:
            return None
        return InsuranceCompanyInDB(**insurance_company)

    async def get_all_insurance_companies(self) -> List[InsuranceCompanyInDB]:
        insurance_companies_records = await self.db.fetch_all(query=GET_ALL_INSURANCE_COMPANIES_QUERY)
        return [InsuranceCompanyInDB(**l) for l in insurance_companies_records]
