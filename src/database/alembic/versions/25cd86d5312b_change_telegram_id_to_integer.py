"""change_telegram_id_to_integer

Revision ID: 25cd86d5312b
Revises: 20240717_add_os_column
Create Date: 2025-07-23 07:43:25.890697

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25cd86d5312b"
down_revision: Union[str, Sequence[str], None] = "20240717_add_os_column"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем тип колонки telegram_id с VARCHAR на INTEGER
    op.execute(
        "ALTER TABLE users ALTER COLUMN telegram_id TYPE INTEGER USING telegram_id::integer"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем тип колонки telegram_id обратно к VARCHAR
    op.execute("ALTER TABLE users ALTER COLUMN telegram_id TYPE VARCHAR")
