"""add_loadout_to_users

Revision ID: 0dd1a20b7ae4
Revises: 26b136ecf4ca
Create Date: 2025-11-08 15:11:07.236002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dd1a20b7ae4'
down_revision: Union[str, Sequence[str], None] = '26b136ecf4ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('loadout', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'loadout')
