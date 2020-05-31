"""empty message

Revision ID: eb07dba98923
Revises: acad84e7d14f
Create Date: 2020-04-14 12:24:31.483327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb07dba98923'
down_revision = 'acad84e7d14f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_profile_picture', table_name='user')
    op.drop_column('user', 'profile_picture')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('profile_picture', sa.VARCHAR(length=20), nullable=True))
    op.create_index('ix_user_profile_picture', 'user', ['profile_picture'], unique=False)
    # ### end Alembic commands ###