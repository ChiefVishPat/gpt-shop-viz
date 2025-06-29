"""initial schema

Revision ID: 0001_initial_schema
Revises:
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
        ),
    )
    op.create_table(
        'snapshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'product_id',
            sa.Integer(),
            sa.ForeignKey('products.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column(
            'captured_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('NOW()'),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('snapshots')
    op.drop_table('products')
