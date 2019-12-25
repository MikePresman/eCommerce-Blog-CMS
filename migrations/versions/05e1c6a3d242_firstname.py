"""firstname

Revision ID: 05e1c6a3d242
Revises: 9f049c81bb2e
Create Date: 2019-03-02 17:54:37.879227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05e1c6a3d242'
down_revision = '9f049c81bb2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Integer(), nullable=True),
    sa.Column('product_title', sa.String(length=100), nullable=True),
    sa.Column('price', sa.String(length=50), nullable=True),
    sa.Column('quantity', sa.String(length=50), nullable=True),
    sa.Column('quantity_left', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('image_associated', sa.String(length=120), nullable=True),
    sa.Column('date_of_event', sa.String(length=120), nullable=True),
    sa.Column('location', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('concert_sale')
    op.add_column('user', sa.Column('first_name', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    op.create_table('concert_sale',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('active', sa.INTEGER(), nullable=True),
    sa.Column('product_title', sa.VARCHAR(length=100), nullable=True),
    sa.Column('price', sa.VARCHAR(length=50), nullable=True),
    sa.Column('quantity', sa.VARCHAR(length=50), nullable=True),
    sa.Column('quantity_left', sa.VARCHAR(length=50), nullable=True),
    sa.Column('description', sa.VARCHAR(length=256), nullable=True),
    sa.Column('image_associated', sa.VARCHAR(length=120), nullable=True),
    sa.Column('date_of_event', sa.VARCHAR(length=120), nullable=True),
    sa.Column('location', sa.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('shop')
    # ### end Alembic commands ###