"""MOAR RAWR

Revision ID: 504e573da6ec
Revises: 590ca21fdbd5
Create Date: 2019-02-12 21:47:22.358200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '504e573da6ec'
down_revision = '590ca21fdbd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('store', sa.Column('quantity', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###