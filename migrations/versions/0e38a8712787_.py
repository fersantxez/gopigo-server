"""empty message

Revision ID: 0e38a8712787
Revises: a4804104c499
Create Date: 2018-02-08 01:33:34.932846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e38a8712787'
down_revision = 'a4804104c499'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('type', sa.String(length=64), nullable=True),
    sa.Column('extension', sa.String(length=64), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=512), nullable=True),
    sa.Column('body', sa.LargeBinary(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_extension'), 'document', ['extension'], unique=False)
    op.create_index(op.f('ix_document_location'), 'document', ['location'], unique=False)
    op.create_index(op.f('ix_document_name'), 'document', ['name'], unique=False)
    op.create_index(op.f('ix_document_type'), 'document', ['type'], unique=False)
    op.add_column(u'user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column(u'user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    op.add_column(u'user', sa.Column('social_id', sa.String(length=64), nullable=True))
    op.alter_column(u'user', 'email',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.create_unique_constraint(None, 'user', ['social_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.alter_column(u'user', 'email',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column(u'user', 'social_id')
    op.drop_column(u'user', 'last_seen')
    op.drop_column(u'user', 'about_me')
    op.drop_index(op.f('ix_document_type'), table_name='document')
    op.drop_index(op.f('ix_document_name'), table_name='document')
    op.drop_index(op.f('ix_document_location'), table_name='document')
    op.drop_index(op.f('ix_document_extension'), table_name='document')
    op.drop_table('document')
    # ### end Alembic commands ###