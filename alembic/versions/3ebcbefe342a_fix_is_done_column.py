"""Fix is_done column

Revision ID: 3ebcbefe342a
Revises: 74a20bf3cadc
Create Date: 2024-04-26 12:16:24.273540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ebcbefe342a'
down_revision: Union[str, None] = '74a20bf3cadc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('request_tasks', 'is_done',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('request_tasks', 'is_done',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
