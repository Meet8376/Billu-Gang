"""
001 Initial Schema for Sessions, MemoryItems, SymbolIndex, and CallGraph

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-07
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('repo_path', sa.String(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
    )

def downgrade():
    op.drop_table('sessions')
