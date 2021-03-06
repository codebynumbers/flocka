"""custom config

Revision ID: 5e420a18d0d7
Revises: 8dfe97bc577d
Create Date: 2019-07-23 15:01:48.434198

"""

# revision identifiers, used by Alembic.
revision = '5e420a18d0d7'
down_revision = '8dfe97bc577d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('branches', sa.Column('custom_config', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('branches', 'custom_config')
    # ### end Alembic commands ###
