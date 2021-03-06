"""empty message

Revision ID: 3504af55fe85
Revises: ccbada1de72d
Create Date: 2022-02-11 10:47:50.423371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3504af55fe85'
down_revision = 'ccbada1de72d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('can_download', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('can_edit', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))

    op.execute("UPDATE users SET can_download = true")
    op.execute("UPDATE users SET can_edit = true")
    op.execute("UPDATE users SET email = ''")
    op.execute("UPDATE users SET is_admin = true")

    op.alter_column('users', 'can_download', nullable=False)
    op.alter_column('users', 'can_edit', nullable=False)
    op.alter_column('users', 'email', nullable=False)
    op.alter_column('users', 'is_admin', nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'email')
    op.drop_column('users', 'can_edit')
    op.drop_column('users', 'can_download')
    # ### end Alembic commands ###
