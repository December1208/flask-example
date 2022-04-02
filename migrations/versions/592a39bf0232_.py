"""empty message

Revision ID: 592a39bf0232
Revises: ac36d0f7684d
Create Date: 2022-04-02 16:56:25.126705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '592a39bf0232'
down_revision = 'ac36d0f7684d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_relation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.Integer(), nullable=True),
    sa.Column('content_type', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_relation_content_type'), 'event_relation', ['content_type'], unique=False)
    op.create_index(op.f('ix_event_relation_event_id'), 'event_relation', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_relation_object_id'), 'event_relation', ['object_id'], unique=False)
    op.create_index(op.f('ix_event_relation_uuid'), 'event_relation', ['uuid'], unique=True)
    op.create_table('event_schedule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.Integer(), nullable=True),
    sa.Column('event_type', sa.Integer(), nullable=True),
    sa.Column('event_params', sa.JSON(), nullable=True),
    sa.Column('trigger_time', sa.Integer(), nullable=True),
    sa.Column('done_time', sa.Integer(), nullable=True),
    sa.Column('event_status', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_schedule_event_status'), 'event_schedule', ['event_status'], unique=False)
    op.create_index(op.f('ix_event_schedule_event_type'), 'event_schedule', ['event_type'], unique=False)
    op.create_index(op.f('ix_event_schedule_trigger_time'), 'event_schedule', ['trigger_time'], unique=False)
    op.create_index(op.f('ix_event_schedule_uuid'), 'event_schedule', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_event_schedule_uuid'), table_name='event_schedule')
    op.drop_index(op.f('ix_event_schedule_trigger_time'), table_name='event_schedule')
    op.drop_index(op.f('ix_event_schedule_event_type'), table_name='event_schedule')
    op.drop_index(op.f('ix_event_schedule_event_status'), table_name='event_schedule')
    op.drop_table('event_schedule')
    op.drop_index(op.f('ix_event_relation_uuid'), table_name='event_relation')
    op.drop_index(op.f('ix_event_relation_object_id'), table_name='event_relation')
    op.drop_index(op.f('ix_event_relation_event_id'), table_name='event_relation')
    op.drop_index(op.f('ix_event_relation_content_type'), table_name='event_relation')
    op.drop_table('event_relation')
    # ### end Alembic commands ###
