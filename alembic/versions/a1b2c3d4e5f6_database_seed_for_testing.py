"""database seed for testing

Revision ID: a1b2c3d4e5f6
Revises: 9b63e8231283
Create Date: 2025-10-04 06:10:00.000000
"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9b63e8231283"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("id", sa.UUID()),
        sa.column("first_name", sa.String(50)),
        sa.column("last_name", sa.String(50)),
        sa.column("card_number", sa.CHAR(6)),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": str(uuid.uuid4()),
                "first_name": "Jan",
                "last_name": "Kowalski",
                "card_number": "111111",
            },
            {
                "id": str(uuid.uuid4()),
                "first_name": "Anna",
                "last_name": "Nowak",
                "card_number": "222222",
            },
            {
                "id": str(uuid.uuid4()),
                "first_name": "Piotr",
                "last_name": "Wiśniewski",
                "card_number": "333333",
            },
        ],
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM users WHERE card_number IN ('111111','222222','333333')"))
