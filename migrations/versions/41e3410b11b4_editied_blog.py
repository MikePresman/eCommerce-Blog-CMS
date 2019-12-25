"""editied blog

Revision ID: 41e3410b11b4
Revises: 95fb0f36e0eb
Create Date: 2019-01-30 20:07:48.070387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41e3410b11b4'
down_revision = '95fb0f36e0eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=True),
    sa.Column('image_link', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('date', sa.String(length=120), nullable=True),
    sa.Column('author', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_title'), 'blog', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_blog_title'), table_name='blog')
    op.drop_table('blog')
    # ### end Alembic commands ###
