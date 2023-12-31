"""added usermixin

Revision ID: 7dede832ea44
Revises: b0a2e9c20bf0
Create Date: 2023-10-30 15:09:32.613336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7dede832ea44'
down_revision = 'b0a2e9c20bf0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('_alembic_tmp_users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=30), nullable=False),
    sa.Column('email', sa.VARCHAR(length=50), nullable=False),
    sa.Column('date_added', sa.DATETIME(), nullable=True),
    sa.Column('password_hash', sa.VARCHAR(length=20), nullable=True),
    sa.Column('username', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username', name='unique_username_constraint')
    )
    # ### end Alembic commands ###
