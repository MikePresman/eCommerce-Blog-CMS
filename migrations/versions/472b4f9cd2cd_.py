"""empty message

Revision ID: 472b4f9cd2cd
Revises: 1fa2c662d7aa
Create Date: 2019-08-03 19:14:41.904394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '472b4f9cd2cd'
down_revision = '1fa2c662d7aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('concert_receipt', sa.Column('concert_id_associated', sa.Integer(), nullable=True))
    op.add_column('concert_receipt', sa.Column('receipt_id', sa.Integer(), nullable=True))
    op.add_column('concert_receipt', sa.Column('user_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('concert_receipt', 'user_id')
    op.drop_column('concert_receipt', 'receipt_id')
    op.drop_column('concert_receipt', 'concert_id_associated')
    # ### end Alembic commands ###
