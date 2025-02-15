"""Added filament inventory model

Revision ID: 14ac243eb593
Revises: cde849534687
Create Date: 2023-11-22 04:14:40.009497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14ac243eb593'
down_revision = 'cde849534687'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('filament_inventory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sku', sa.String(length=150), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sku'),
    sa.UniqueConstraint('sku', name='uq_filament_inventory_sku')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('filament_inventory')
    # ### end Alembic commands ###
