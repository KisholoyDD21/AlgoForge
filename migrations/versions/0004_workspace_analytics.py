"""Add persistent code drafts, version history and custom test metadata.

Revision ID: 0004_workspace_analytics
Revises: 0003_discussions
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from app.main import Base

revision = "0004_workspace_analytics"
down_revision = "0003_discussions"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if "submissions" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("submissions")}
        if "custom_test_cases" not in columns:
            op.add_column("submissions", sa.Column("custom_test_cases", sa.JSON(), nullable=True))
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    for table in ("code_draft_versions", "code_drafts"):
        if table in inspector.get_table_names():
            op.drop_table(table)
    if "submissions" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("submissions")}
        if "custom_test_cases" in columns:
            op.drop_column("submissions", "custom_test_cases")
