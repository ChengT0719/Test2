"""empty message

Revision ID: 9c75a5cbf319
Revises: 7621c57f1de2
Create Date: 2020-03-16 18:06:00.398977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c75a5cbf319'
down_revision = '7621c57f1de2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('suggestion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('suggestion', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_add_time'), 'user', ['add_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_add_time'), table_name='user')
    op.drop_table('suggestion')
    # ### end Alembic commands ###
