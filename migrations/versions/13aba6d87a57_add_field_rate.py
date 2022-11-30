"""add field rate

Revision ID: 13aba6d87a57
Revises: 67923f66da37
Create Date: 2022-11-30 21:10:29.040968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13aba6d87a57'
down_revision = '67923f66da37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quote_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rate', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quote_model', schema=None) as batch_op:
        batch_op.drop_column('rate')

    # ### end Alembic commands ###
