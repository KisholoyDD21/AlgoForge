"""Add native problem judging and scheduled contests.

Revision ID: 0002_judging_contests
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.main import Base

revision = "0002_judging_contests"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    # 0001 imports the current metadata, so fresh installations may already have
    # these columns. Existing installations receive only the missing columns.
    if "problems" in tables:
        columns = {c["name"] for c in inspector.get_columns("problems")}
        additions = [
            sa.Column("is_native", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("constraints", sa.Text(), nullable=False, server_default=""),
            sa.Column("examples", sa.JSON(), nullable=True),
            sa.Column("hints", sa.JSON(), nullable=True),
        ]
        for column in additions:
            if column.name not in columns:
                op.add_column("problems", column)
    if "submissions" in tables:
        columns = {c["name"] for c in inspector.get_columns("submissions")}
        additions = [
            sa.Column("judge_tokens", sa.JSON(), nullable=True),
            sa.Column("case_results", sa.JSON(), nullable=True),
            sa.Column("contest_id", sa.Integer(), nullable=True),
        ]
        for column in additions:
            if column.name not in columns:
                op.add_column("submissions", column)
    # Create new tables for test cases, contests and daily challenge records.
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    for table in ("daily_challenges", "contest_participants", "contest_problems", "contests", "problem_test_cases"):
        if table in tables:
            op.drop_table(table)
    for table, columns in {
        "submissions": ("contest_id", "case_results", "judge_tokens"),
        "problems": ("hints", "examples", "constraints", "is_native"),
    }.items():
        if table in tables:
            current = {c["name"] for c in inspect(bind).get_columns(table)}
            for column in columns:
                if column in current:
                    op.drop_column(table, column)
