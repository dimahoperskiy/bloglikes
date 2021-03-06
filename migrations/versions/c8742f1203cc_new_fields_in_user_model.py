"""new fields in user model

Revision ID: c8742f1203cc
Revises: 2cafa6f25899
Create Date: 2020-04-14 12:45:55.351366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8742f1203cc'
down_revision = '2cafa6f25899'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('ava', sa.String(length=20), nullable=True))
    op.create_index(op.f('ix_user_ava'), 'user', ['ava'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_ava'), table_name='user')
    op.drop_column('user', 'ava')
    # ### end Alembic commands ###
