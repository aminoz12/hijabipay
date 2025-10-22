"""Add delivery_cost to PaymentLink model

Revision ID: 1234567890ab
Revises: 477e3eb9e659
Create Date: 2023-10-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '477e3eb9e659'
branch_labels = None
depends_on = None

def upgrade():
    # Add delivery_cost column with default 0.0
    op.add_column('payment_link', sa.Column('delivery_cost', sa.Float(), nullable=False, server_default='0.0'))
    # Update existing rows to have 0.0 as delivery_cost
    op.execute('UPDATE payment_link SET delivery_cost = 0.0')

def downgrade():
    # Drop the delivery_cost column
    op.drop_column('payment_link', 'delivery_cost')
