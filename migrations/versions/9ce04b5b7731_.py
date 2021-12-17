"""empty message

Revision ID: 9ce04b5b7731
Revises: 12cb51a033c9
Create Date: 2021-07-10 14:51:57.304027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ce04b5b7731'
down_revision = '12cb51a033c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hazard',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hazard_subtype', sa.String(length=65), nullable=True),
    sa.Column('hazard_type', sa.String(length=35), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['point.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # op.drop_table('spatial_ref_sys')
    op.add_column('point', sa.Column('suggested_solution', sa.String(length=300), nullable=True))
    # op.drop_index('idx_point_geom', table_name='point')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_index('idx_point_geom', 'point', ['geom'], unique=False)
    op.drop_column('point', 'suggested_solution')
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    # sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    # )
    op.drop_table('hazard')
    # ### end Alembic commands ###