"""add_user_type_column

Revision ID: e7c09e5eb722
Revises: 5af87c634130
Create Date: 2025-08-14 21:55:42.617671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7c09e5eb722'
down_revision: Union[str, Sequence[str], None] = '5af87c634130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add user_type column with default value
    op.add_column('users', sa.Column('user_type', sa.String(), nullable=True))
    # Set default value for existing users
    op.execute("UPDATE users SET user_type = 'authenticated' WHERE user_type IS NULL")
    # Make column non-nullable after setting defaults
    op.alter_column('users', 'user_type', nullable=False, server_default='authenticated')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'user_type')
