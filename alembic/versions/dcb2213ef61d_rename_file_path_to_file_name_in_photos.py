"""rename file_path to file_name in photos

Revision ID: dcb2213ef61d
Revises: 5d46078e9a7f
Create Date: 2026-02-21 12:14:48.175535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcb2213ef61d'
down_revision: Union[str, Sequence[str], None] = '5d46078e9a7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "photos",
        "file_path",
        new_column_name="file_name",
    )


def downgrade() -> None:
    op.alter_column(
        "photos",
        "file_name",
        new_column_name="file_path",
    )
