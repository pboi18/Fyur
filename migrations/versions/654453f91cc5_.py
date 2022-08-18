"""empty message

Revision ID: 654453f91cc5
Revises: 6070b11acb60
Create Date: 2022-08-18 15:01:13.499405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '654453f91cc5'
down_revision = '6070b11acb60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('genre')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('venue_genres', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['venue_genres'], ['venue.id'], name='genre_venue_genres_fkey'),
    sa.PrimaryKeyConstraint('id', name='genre_pkey')
    )
    # ### end Alembic commands ###
