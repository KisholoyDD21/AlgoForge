"""Add problem discussions, comments, votes and moderation reports.

Revision ID: 0003_discussions
Revises: 0002_judging_contests
"""
from alembic import op
from app.main import Base

revision = "0003_discussions"
down_revision = "0002_judging_contests"
branch_labels = None
depends_on = None


def upgrade():
    # Older installs gain the new tables; fresh installs may already have them
    # because the existing baseline migrations use current Base metadata.
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade():
    bind = op.get_bind()
    for table in ("discussion_reports", "discussion_votes", "discussion_comments", "discussions"):
        op.drop_table(table)
