"""empty message

Revision ID: bd76967127d0
Revises: 8be9344b4d8b
Create Date: 2019-02-20 19:29:43.206815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd76967127d0'
down_revision = '8be9344b4d8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email_verified', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'email_verified')
    # ### end Alembic commands ###
