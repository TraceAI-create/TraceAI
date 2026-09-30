"""enable_rls_on_public_tables

Revision ID: 67a5ddc91725
Revises: 10b8a6fdf10d
Create Date: 2026-09-30 11:21:26.269672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67a5ddc91725'
down_revision: Union[str, Sequence[str], None] = '10b8a6fdf10d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = [
    "alembic_version",
    "decisions",
    "audit_events",
    "policies",
    "decision_evidence",
    "evidence",
    "review_actions",
    "replay_runs",
]


def upgrade() -> None:
    """Enable Row Level Security on all public tables to secure PostgREST access."""
    for table in TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Disable Row Level Security on all public tables."""
    for table in TABLES:
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")
