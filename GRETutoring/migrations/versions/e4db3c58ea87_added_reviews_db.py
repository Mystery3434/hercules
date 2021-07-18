"""Added Reviews DB

Revision ID: e4db3c58ea87
Revises: 9d6b3d3e367d
Create Date: 2021-07-18 16:46:11.094333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4db3c58ea87'
down_revision = '9d6b3d3e367d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('review_text', sa.Text(), nullable=False),
    sa.Column('date_time', sa.DateTime(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('tutor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['tutor_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review')
    # ### end Alembic commands ###
