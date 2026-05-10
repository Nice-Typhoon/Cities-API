from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    #Включаем расширение postgis
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    #индекс
    op.create_index(
        "ix_cities_name_lower",
        "cities",
        [sa.text("lower(name)")],
    )

    op.execute("""
        ALTER TABLE cities
        ADD COLUMN location geography(POINT, 4326)
        GENERATED ALWAYS AS (
            ST_SetSRID(ST_MakePoint(longitude::float8, latitude::float8), 4326)::geography
        ) STORED
    """)

    op.create_index(
        "ix_cities_location_gist",
        "cities",
        ["location"],
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index("ix_cities_location_gist", table_name="cities")
    op.drop_index("ix_cities_name_lower", table_name="cities")
    op.drop_table("cities")
