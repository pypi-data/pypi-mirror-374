"""add_protocol_enablement_flags_to_tunnel_config

Revision ID: c8f9d2e5a1b3
Revises: b4d7e8f5c1a2
Create Date: 2025-07-09 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f9d2e5a1b3'
down_revision: Union[str, None] = 'b4d7e8f5c1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ospf_enabled and ebgp_enabled boolean columns to tunnel_config_data table."""
    # Add ospf_enabled column
    op.add_column('tunnel_config_data', sa.Column(
        'ospf_enabled', 
        sa.Boolean(), 
        nullable=True,
        comment='Whether OSPF protocol is enabled for this configuration'
    ))
    
    # Add ebgp_enabled column
    op.add_column('tunnel_config_data', sa.Column(
        'ebgp_enabled', 
        sa.Boolean(), 
        nullable=True,
        comment='Whether eBGP protocol is enabled for this configuration'
    ))
    
    # Set default values for existing records
    op.execute("UPDATE tunnel_config_data SET ospf_enabled = false WHERE ospf_enabled IS NULL")
    op.execute("UPDATE tunnel_config_data SET ebgp_enabled = false WHERE ebgp_enabled IS NULL")


def downgrade() -> None:
    """Remove ospf_enabled and ebgp_enabled columns from tunnel_config_data table."""
    op.drop_column('tunnel_config_data', 'ebgp_enabled')
    op.drop_column('tunnel_config_data', 'ospf_enabled')
