"""Added Reviews DB and added score field

Revision ID: 6178a238c2a4
Revises: e4db3c58ea87
Create Date: 2021-07-18 16:55:35.860058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6178a238c2a4'
down_revision = 'e4db3c58ea87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('review', sa.Column('review_score', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('review', 'review_score')
    # ### end Alembic commands ###