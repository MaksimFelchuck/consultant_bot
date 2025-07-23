"""add os column to products

Revision ID: 20240717_add_os_column
Revises: ee48eb4ce95e
Create Date: 2024-07-17 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240717_add_os_column"
down_revision = "ee48eb4ce95e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("products", sa.Column("os", sa.String(), index=True))


def downgrade():
    op.drop_column("products", "os")
