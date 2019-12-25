"""updated store';


Revision ID: ab4ded39755e
Revises: bdf84db37307
Create Date: 2019-02-12 20:34:40.918280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab4ded39755e'
down_revision = 'bdf84db37307'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass    

    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('store', sa.Column('quantity', sa.INTEGER(), nullable=True))
    op.drop_column('store', 'quantity_left')
    op.drop_column('store', 'product_title')
    # ### end Alembic commands ###