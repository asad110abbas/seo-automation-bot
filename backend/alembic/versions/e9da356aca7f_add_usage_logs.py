"""add_usage_logs

Revision ID: e9da356aca7f
Revises: 500fc64cea15
Create Date: 2026-06-11 06:49:39.408015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9da356aca7f'
down_revision = '500fc64cea15'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'usage_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=True),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('input_cost_usd', sa.Float(), nullable=False),
        sa.Column('output_cost_usd', sa.Float(), nullable=False),
        sa.Column('serp_calls', sa.Integer(), nullable=False),
        sa.Column('serp_cost_usd', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('usage_logs')
