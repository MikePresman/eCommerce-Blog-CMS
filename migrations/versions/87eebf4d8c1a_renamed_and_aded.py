"""renamed and aded

Revision ID: 87eebf4d8c1a
Revises: 05e1c6a3d242
Create Date: 2019-03-04 15:24:02.454368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87eebf4d8c1a'
down_revision = '05e1c6a3d242'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('concert_shop',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Integer(), nullable=True),
    sa.Column('concert_title', sa.String(length=100), nullable=True),
    sa.Column('price', sa.String(length=50), nullable=True),
    sa.Column('quantity', sa.String(length=50), nullable=True),
    sa.Column('quantity_left', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('image_associated', sa.String(length=120), nullable=True),
    sa.Column('date_of_event', sa.String(length=120), nullable=True),
    sa.Column('location', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('shop')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop',
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
    op.drop_table('concert_shop')
    # ### end Alembic commands ###
