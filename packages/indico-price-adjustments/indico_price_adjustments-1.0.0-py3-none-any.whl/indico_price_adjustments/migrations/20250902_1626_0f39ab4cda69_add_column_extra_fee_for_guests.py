"""add column extra_fee_for_guests

Revision ID: 0f39ab4cda69
Revises: 
Create Date: 2025-09-02 16:26:14.472990
"""

import sqlalchemy as sa
from alembic import op

from sqlalchemy.sql.ddl import CreateSchema, DropSchema


# revision identifiers, used by Alembic.
revision = '0f39ab4cda69'
down_revision = None
branch_labels = None
depends_on = None



def upgrade():# Add the column as nullable first
    op.add_column('forms', sa.Column('extra_fee_for_guests', sa.Numeric(precision=11, scale=2), nullable=True), schema='event_registration')
    # Set default value for existing rows
    op.execute("UPDATE event_registration.forms SET extra_fee_for_guests = 0 WHERE extra_fee_for_guests IS NULL")
    # Alter column to be non-nullable
    op.alter_column('forms', 'extra_fee_for_guests', nullable=False, schema='event_registration')


def downgrade():
    op.drop_column('forms', 'extra_fee_for_guests', schema='event_registration')
