"""added username

Revision ID: b0a2e9c20bf0
Revises: ffe3fce899e0
Create Date: 2023-10-30 12:53:44.037233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0a2e9c20bf0'
down_revision = 'ffe3fce899e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(), nullable=False))
        batch_op.create_unique_constraint('unique_username_constraint', ['username'])  # Add a name for the unique constraint
        batch_op.drop_column('username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_color', sa.VARCHAR(length=30), nullable=True))
        batch_op.drop_constraint('unique_username_constraint', type_='unique')  # Specify the name of the unique constraint to drop
        batch_op.drop_column('username')

    # ### end Alembic commands ###
