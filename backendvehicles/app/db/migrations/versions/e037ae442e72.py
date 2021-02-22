"""

Revision ID: e037ae442e72
Revises:
Create Date: 2020-02-01 10:41:35.468471

"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic
revision = 'e037ae442e72'
down_revision = None
branch_labels = None
depends_on = None


def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )


def timestamps() -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def create_vehicles_table() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("sign", sa.Text, nullable=False, index=True, unique=True),
        sa.Column("type", sa.Text, nullable=False, server_default="car"),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("manufacture_year", sa.Integer, nullable=False),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_vehicle_modtime
            BEFORE UPDATE
            ON vehicles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_insurance_company_table() -> None:
    op.create_table(
        "insurance_company",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False, index=True, unique=True),
        sa.Column("email", sa.Text, nullable=False),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_insurance_company_modtime
            BEFORE UPDATE
            ON insurance_company
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """

    )


def create_insurance_table() -> None:
    op.create_table(
        "insurance",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("number", sa.Text, index=True),
        sa.Column("expire_date", sa.DateTime),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey('vehicles.id', ondelete="CASCADE")),
        sa.Column("insurance_company_id", sa.Integer, sa.ForeignKey('insurance_company.id')),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_insurance_modtime
            BEFORE UPDATE
            ON insurance
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        INSERT INTO insurance_company(id,name,email)
        VALUES (0, 'Insurance Company Name', 'providevalidem@il.inc')
        """
    )

def create_role_vehicle_user_table() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("role", sa.Text),
        sa.Column("user_id", sa.Integer),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey('vehicles.id', ondelete="CASCADE")),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_roles_modtime
            BEFORE UPDATE
            ON roles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_accident_table() -> None:
    op.create_table(
        "accident",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", , sa.DateTime, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_accident_modtime
            BEFORE UPDATE
            ON accident
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """

    )

def create_accident_statement_table() -> None:
    op.create_table(
        "accident_statement",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("vehicle_sign", , sa.DateTime, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_accident_modtime
            BEFORE UPDATE
            ON accident
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """

    )

def upgrade() -> None:
    create_updated_at_trigger()
    create_vehicles_table()
    create_insurance_company_table()
    create_insurance_table()
    create_role_vehicle_user_table()
	
def downgrade() -> None:
    op.drop_table("roles")
    op.drop_table('insurance')
    op.drop_table('insurance_company')
    op.drop_table('vehicles')
    op.execute("DROP FUNCTION update_updated_at_column")

