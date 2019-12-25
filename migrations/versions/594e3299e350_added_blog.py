"""added blog

Revision ID: 594e3299e350
Revises: 7e53000ddb29
Create Date: 2019-09-02 20:54:34.653791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '594e3299e350'
down_revision = '7e53000ddb29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('date_posted', sa.String(length=120), nullable=True),
    sa.Column('reply', sa.Integer(), nullable=True),
    sa.Column('reply_to', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['reply_to'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blog_comment')
    # ### end Alembic commands ###
