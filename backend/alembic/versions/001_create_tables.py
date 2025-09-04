from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import uuid

revision = '001_create_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('user_uuid', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
        sa.Column('username', sa.String, unique=True, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('deleted_date', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_deleted_date', 'users', ['deleted_date'])
    op.create_table(
        'tasks',
        sa.Column('task_uuid', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', ARRAY(sa.String), nullable=True),
        sa.Column('status', sa.String, nullable=False, default='To Do'),
        sa.Column('priority', sa.Integer, nullable=False, default=2),
        sa.Column('assigned_to', UUID(as_uuid=True), sa.ForeignKey('users.user_uuid'), nullable=True),
        sa.Column('deleted_date', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_deleted_date', 'tasks', ['deleted_date'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
