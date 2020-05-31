"""empty message

Revision ID: 139f974168fe
Revises: eb07dba98923
Create Date: 2020-04-14 12:25:46.021141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '139f974168fe'
down_revision = 'eb07dba98923'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'profile_picture')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_picture', sa.VARCHAR(length=20), nullable=True))
    # ### end Alembic commands ###
