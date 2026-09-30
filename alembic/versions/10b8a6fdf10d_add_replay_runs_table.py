"""Add replay_runs table.

Revision ID: 10b8a6fdf10d
Revises: b5998826aa05
Create Date: 2026-09-30 10:21:27.581227
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers used by Alembic
revision: str = '10b8a6fdf10d'
down_revision: Union[str, Sequence[str], None] = 'b5998826aa05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the replay_runs table."""
    op.create_table('replay_runs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('decision_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('replay_mode', sa.String(length=50), nullable=False),
    sa.Column('similarity_score', sa.Float(), nullable=False),
    sa.Column('diff_summary', sa.JSON(), nullable=False),
    sa.Column('replayed_events', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['decision_id'], ['decisions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop the replay_runs table."""
    op.drop_table('replay_runs')
