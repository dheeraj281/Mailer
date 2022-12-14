"""empty message

Revision ID: 1641d90aed60
Revises: 2075585fe061
Create Date: 2022-08-14 17:06:03.613856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1641d90aed60'
down_revision = '2075585fe061'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('running_status', sa.Boolean(), nullable=True),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('job_log')
    # ### end Alembic commands ###
