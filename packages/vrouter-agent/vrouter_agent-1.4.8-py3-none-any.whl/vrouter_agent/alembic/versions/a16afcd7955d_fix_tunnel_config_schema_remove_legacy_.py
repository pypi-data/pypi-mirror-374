"""Fix tunnel config schema - remove legacy status columns only

Revision ID: a16afcd7955d
Revises: 
Create Date: 2025-06-06 17:44:21.163143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a16afcd7955d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove legacy status columns and fix schema mismatch.
    
    Current state:
    - tunnel_config_data has: status (legacy), state, config_data_state  
    - tunnel_config_history has: old_status, new_status (legacy), old_config_data_state, new_config_data_state
    
    Target state:
    - tunnel_config_data has: state (NOT NULL), config_data_state (NOT NULL)
    - tunnel_config_history has: old_state, new_state (NOT NULL), old_config_data_state, new_config_data_state (NOT NULL)
    """
    
    # Step 1: Migrate data from status to state in tunnel_config_data
    # First, copy data from status to state where state is null or default
    op.execute("""
        UPDATE tunnel_config_data 
        SET state = CASE 
            WHEN status = 'completed' THEN 'active'
            WHEN status = 'failed' THEN 'error' 
            WHEN status = 'processing' THEN 'pending'
            WHEN status = 'pending' THEN 'planned'
            ELSE 'planned'
        END
        WHERE state IS NULL OR state = 'planned'
    """)
    
    # Step 2: Migrate data from old_status/new_status to old_state/new_state in tunnel_config_history
    # Add the new state columns first
    with op.batch_alter_table('tunnel_config_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('old_state', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('new_state', sa.VARCHAR(), nullable=True))
    
    # Copy data from status columns to state columns
    op.execute("""
        UPDATE tunnel_config_history 
        SET old_state = CASE 
            WHEN old_status = 'completed' THEN 'active'
            WHEN old_status = 'failed' THEN 'error'
            WHEN old_status = 'processing' THEN 'pending' 
            WHEN old_status = 'pending' THEN 'planned'
            ELSE old_status
        END,
        new_state = CASE
            WHEN new_status = 'completed' THEN 'active'
            WHEN new_status = 'failed' THEN 'error'
            WHEN new_status = 'processing' THEN 'pending'
            WHEN new_status = 'pending' THEN 'planned' 
            ELSE new_status
        END
    """)
    
    # Set default values for null new_state
    op.execute("UPDATE tunnel_config_history SET new_state = 'planned' WHERE new_state IS NULL")
    
    # Step 3: Make state and config_data_state NOT NULL in tunnel_config_data
    with op.batch_alter_table('tunnel_config_data', schema=None) as batch_op:
        batch_op.alter_column('state', nullable=False, existing_server_default=sa.text("'planned'"))
        batch_op.alter_column('config_data_state', nullable=False, existing_server_default=sa.text("'pending'"))
        batch_op.drop_column('status')  # Remove legacy status column
    
    # Step 4: Make new_state and new_config_data_state NOT NULL in tunnel_config_history  
    with op.batch_alter_table('tunnel_config_history', schema=None) as batch_op:
        batch_op.alter_column('new_state', nullable=False)
        batch_op.alter_column('new_config_data_state', nullable=False, existing_server_default=sa.text("'pending'"))
        batch_op.drop_column('old_status')   # Remove legacy status columns
        batch_op.drop_column('new_status')


def downgrade() -> None:
    """
    Restore legacy status columns (for rollback purposes).
    """
    
    # Step 1: Add back the legacy status column to tunnel_config_data
    with op.batch_alter_table('tunnel_config_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.VARCHAR(), nullable=False, server_default='pending'))
        batch_op.alter_column('state', nullable=True)
        batch_op.alter_column('config_data_state', nullable=True)
    
    # Copy state back to status
    op.execute("""
        UPDATE tunnel_config_data 
        SET status = CASE 
            WHEN state = 'active' THEN 'completed'
            WHEN state = 'error' THEN 'failed'
            WHEN state = 'pending' THEN 'processing'
            WHEN state = 'planned' THEN 'pending'
            ELSE 'pending'
        END
    """)
    
    # Step 2: Add back legacy status columns to tunnel_config_history
    with op.batch_alter_table('tunnel_config_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('old_status', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('new_status', sa.VARCHAR(), nullable=False, server_default='pending'))
        batch_op.alter_column('new_state', nullable=True)
        batch_op.alter_column('new_config_data_state', nullable=True)
    
    # Copy state back to status  
    op.execute("""
        UPDATE tunnel_config_history 
        SET old_status = CASE 
            WHEN old_state = 'active' THEN 'completed'
            WHEN old_state = 'error' THEN 'failed'
            WHEN old_state = 'pending' THEN 'processing'
            WHEN old_state = 'planned' THEN 'pending'
            ELSE old_state
        END,
        new_status = CASE
            WHEN new_state = 'active' THEN 'completed'
            WHEN new_state = 'error' THEN 'failed'
            WHEN new_state = 'pending' THEN 'processing'
            WHEN new_state = 'planned' THEN 'pending'
            ELSE new_state
        END
    """)
    
    # Step 3: Remove the new state columns
    with op.batch_alter_table('tunnel_config_history', schema=None) as batch_op:
        batch_op.drop_column('old_state')
        batch_op.drop_column('new_state')
