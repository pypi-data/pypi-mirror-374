"""
NAT Configuration Manager

This module provides specialized management for NAT (Network Address Translation)
configurations, implementing security management interfaces.
"""

from typing import List, Dict, Any, Optional
from itertools import chain
import ipaddress

from loguru import logger as log
from vrouter.common import models

from ..base_interfaces import SecurityManager, create_result_dict
from ..connection.vpp_connection import VPPConnectionManager
from ...core.base import Interface


class NATManager(SecurityManager):
    """
    Manages NAT44 configuration through VPP API.
    
    This class handles NAT interface configuration, address pools,
    port mappings, and identity mappings for various protocols.
    """
    
    def __init__(self, connection_manager: VPPConnectionManager):
        """
        Initialize the NAT manager.
        
        Args:
            connection_manager: VPP connection manager instance
        """
        self.connection = connection_manager
        self.active_policies: Dict[str, Dict[str, Any]] = {}
    
    def _extract_reply_errors(self, reply) -> List[str]:
        """Extract all error messages from a VPP reply object."""
        errors = []
        
        # Check processing_error (legacy field)
        if hasattr(reply, 'processing_error') and reply.processing_error:
            errors.append(reply.processing_error)
        
        # Check added_items for errors
        if hasattr(reply, 'added_items'):
            for item in reply.added_items:
                if hasattr(item, 'error') and item.error:
                    errors.append(f"Added item error: {item.error}")
                if hasattr(item, 'state') and 'FAILURE' in str(item.state):
                    errors.append(f"Item state failure: {item.state}")
        
        # Check vpp_apply_attempted_items for detailed errors
        if hasattr(reply, 'vpp_apply_attempted_items'):
            for item in reply.vpp_apply_attempted_items:
                if hasattr(item, 'error') and item.error:
                    errors.append(f"VPP apply error: {item.error}")
                if hasattr(item, 'state') and 'FAILURE' in str(item.state):
                    errors.append(f"VPP apply state failure: {item.state}")
        
        # Check vpp_apply_success flag
        if hasattr(reply, 'vpp_apply_success') and reply.vpp_apply_success is False:
            if not errors:  # Only add generic message if no specific errors found
                errors.append("VPP apply failed without specific error message")
        
        return errors

    def configure_nat(self, lan_interface: Interface, wan_interface: Interface,
                     wg_ports_to_open: List[int], tcp_ports: List[int] = None,
                     udp_ports: List[int] = None) -> bool:
        """
        Configure NAT44 for LAN/WAN interfaces with port mappings.
        
        Args:
            lan_interface: LAN interface configuration
            wan_interface: WAN interface configuration  
            wg_ports_to_open: WireGuard ports to open (UDP)
            tcp_ports: Additional TCP ports to open
            udp_ports: Additional UDP ports to open
            
        Returns:
            bool: True if configuration successful, False otherwise
        """
        try:
            tcp_ports = tcp_ports or []
            udp_ports = udp_ports or []
            
            policy_name = f"nat-{lan_interface.interface_name}-{wan_interface.interface_name}"
            
            log.info(f"Configuring NAT policy '{policy_name}' for {lan_interface.interface_name} -> {wan_interface.interface_name}")
            
            # Create NAT interface configurations
            lan_nat_iface = models.Nat44InterfaceConfigurationItem(
                name=lan_interface.interface_name,
                nat_inside=True,
                nat_outside=False,
                output_feature=False,
            )
            
            wan_nat_iface = models.Nat44InterfaceConfigurationItem(
                name=wan_interface.interface_name,
                nat_inside=False,
                nat_outside=True,
                output_feature=False,
            )
            
            # Create address pool
            nat_address_pool = models.Nat44AddressPoolConfigurationItem(
                name="nat-pool",
                first_ip=ipaddress.IPv4Address(wan_interface.ip_address),
                last_ip=ipaddress.IPv4Address(wan_interface.ip_address),
            )
            
            # Create port mappings
            wg_port_mappings = [
                models.IdentityMapping(
                    interface=wan_interface.interface_name,
                    protocol=models.ProtocolInNAT.UDP,
                    port=port,
                )
                for port in wg_ports_to_open
            ]
            
            tcp_port_mappings = [
                models.IdentityMapping(
                    interface=wan_interface.interface_name,
                    protocol=models.ProtocolInNAT.TCP,
                    port=port,
                )
                for port in tcp_ports
            ]
            
            udp_port_mappings = [
                models.IdentityMapping(
                    interface=wan_interface.interface_name,
                    protocol=models.ProtocolInNAT.UDP,
                    port=port,
                )
                for port in udp_ports
            ]
            
            # Create NAT mappings configuration
            nat_mappings = models.DNat44ConfigurationItem(
                label="nat-mappings",
                static_mappings=[],
                identity_mappings=list(chain(
                    wg_port_mappings, 
                    tcp_port_mappings, 
                    udp_port_mappings
                )),
            )
            
            # Apply configuration to VPP
            reply = self.connection.client.add_configuration(
                lan_nat_iface,
                wan_nat_iface,
                nat_address_pool,
                nat_mappings,
            )
            
            errors = self._extract_reply_errors(reply)
            if errors:
                for error in errors:
                    log.error(f"Error adding NAT configuration: {error}")
                return False
            
            # Store policy information for management
            self.active_policies[policy_name] = {
                'lan_interface': lan_interface.interface_name,
                'wan_interface': wan_interface.interface_name,
                'wg_ports': wg_ports_to_open,
                'tcp_ports': tcp_ports,
                'udp_ports': udp_ports,
                'created_at': self._get_current_timestamp()
            }
            
            log.info(f"NAT configuration '{policy_name}' applied successfully")
            return True
            
        except Exception as e:
            log.error(f"Exception configuring NAT: {e}")
            return False
    
    def remove_nat_configuration(self, lan_interface: Interface, wan_interface: Interface,
                                wg_ports_to_open: List[int], tcp_ports: List[int] = None,
                                udp_ports: List[int] = None) -> bool:
        """
        Remove NAT configuration.
        
        Args:
            lan_interface: LAN interface configuration
            wan_interface: WAN interface configuration
            wg_ports_to_open: WireGuard ports that were opened
            tcp_ports: TCP ports that were opened
            udp_ports: UDP ports that were opened
            
        Returns:
            bool: True if removal successful, False otherwise
        """
        try:
            tcp_ports = tcp_ports or []
            udp_ports = udp_ports or []
            
            policy_name = f"nat-{lan_interface.interface_name}-{wan_interface.interface_name}"
            
            log.info(f"Removing NAT configuration '{policy_name}'")
            
            # Find existing NAT configurations
            current_config = self.connection.client.get_configuration()
            
            nat_configs = [
                item.config
                for item in current_config.items
                if isinstance(item.config, models.Nat44InterfaceConfigurationItem)
                and item.config.name in [lan_interface.interface_name, wan_interface.interface_name]
            ]
            
            # Find port mappings to remove
            all_ports = set(wg_ports_to_open + tcp_ports + udp_ports)
            port_mappings = [
                item.config
                for item in current_config.items
                if isinstance(item.config, models.IdentityMapping)
                and item.config.port in all_ports
            ]
            
            if not nat_configs:
                log.warning("No NAT configuration found to remove")
                return True
            
            # Remove configurations from VPP
            configs_to_remove = nat_configs + port_mappings
            reply = self.connection.client.delete_configuration(*configs_to_remove)
            
            errors = self._extract_reply_errors(reply)
            if errors:
                for error in errors:
                    log.error(f"Error deleting NAT configuration: {error}")
                return False
            
            # Remove from active policies
            if policy_name in self.active_policies:
                del self.active_policies[policy_name]
            
            log.info(f"NAT configuration '{policy_name}' removed successfully")
            return True
            
        except Exception as e:
            log.error(f"Exception removing NAT configuration: {e}")
            return False
    
    # Implementation of SecurityManager abstract methods
    
    def create_policy(self, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a NAT policy from configuration.
        
        Args:
            policy_config: NAT policy configuration
            
        Returns:
            dict: Creation result
        """
        try:
            # Extract configuration parameters
            lan_iface_config = policy_config.get('lan_interface')
            wan_iface_config = policy_config.get('wan_interface')
            ports_config = policy_config.get('ports', {})
            
            if not lan_iface_config or not wan_iface_config:
                return create_result_dict(
                    success=False, 
                    error="Missing required interface configurations"
                )
            
            # Convert to Interface objects
            lan_interface = self._dict_to_interface(lan_iface_config)
            wan_interface = self._dict_to_interface(wan_iface_config)
            
            # Configure NAT
            success = self.configure_nat(
                lan_interface=lan_interface,
                wan_interface=wan_interface,
                wg_ports_to_open=ports_config.get('wireguard', []),
                tcp_ports=ports_config.get('tcp', []),
                udp_ports=ports_config.get('udp', [])
            )
            
            policy_name = f"nat-{lan_interface.interface_name}-{wan_interface.interface_name}"
            
            if success:
                return create_result_dict(
                    success=True,
                    data={'policy_name': policy_name, 'status': 'active'}
                )
            else:
                return create_result_dict(success=False, error="Failed to configure NAT")
                
        except Exception as e:
            log.error(f"Exception creating NAT policy: {e}")
            return create_result_dict(success=False, error=str(e))
    
    def apply_policy(self, policy_name: str) -> bool:
        """
        Apply a NAT policy by name.
        
        Args:
            policy_name: Name of policy to apply
            
        Returns:
            bool: True if applied successfully, False otherwise
        """
        if policy_name not in self.active_policies:
            log.error(f"NAT policy '{policy_name}' not found")
            return False
        
        # Policy is already applied when created in this implementation
        log.info(f"NAT policy '{policy_name}' is already active")
        return True
    
    def remove_policy(self, policy_name: str) -> bool:
        """
        Remove a NAT policy by name.
        
        Args:
            policy_name: Name of policy to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        if policy_name not in self.active_policies:
            log.warning(f"NAT policy '{policy_name}' not found")
            return True
        
        try:
            policy = self.active_policies[policy_name]
            
            # Create Interface objects from stored data
            lan_interface = Interface(interface_name=policy['lan_interface'])
            wan_interface = Interface(interface_name=policy['wan_interface'])
            
            # Remove the NAT configuration
            success = self.remove_nat_configuration(
                lan_interface=lan_interface,
                wan_interface=wan_interface,
                wg_ports_to_open=policy['wg_ports'],
                tcp_ports=policy['tcp_ports'],
                udp_ports=policy['udp_ports']
            )
            
            return success
            
        except Exception as e:
            log.error(f"Exception removing NAT policy '{policy_name}': {e}")
            return False
    
    # Implementation of NetworkComponent abstract methods
    
    def create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create NAT configuration from config."""
        return self.create_policy(config)
    
    def delete(self, identifier: str) -> bool:
        """Delete NAT policy by name."""
        return self.remove_policy(identifier)
    
    def get_status(self, identifier: str) -> Dict[str, Any]:
        """Get status of NAT policy."""
        if identifier in self.active_policies:
            policy = self.active_policies[identifier]
            return {
                'name': identifier,
                'status': 'active',
                'lan_interface': policy['lan_interface'],
                'wan_interface': policy['wan_interface'],
                'ports': {
                    'wireguard': policy['wg_ports'],
                    'tcp': policy['tcp_ports'],
                    'udp': policy['udp_ports']
                },
                'created_at': policy['created_at']
            }
        else:
            return {'name': identifier, 'status': 'not_found'}
    
    def list_components(self) -> List[Dict[str, Any]]:
        """List all active NAT policies."""
        return [
            {
                'name': name,
                'status': 'active',
                'lan_interface': policy['lan_interface'],
                'wan_interface': policy['wan_interface'],
                'port_count': len(policy['wg_ports']) + len(policy['tcp_ports']) + len(policy['udp_ports'])
            }
            for name, policy in self.active_policies.items()
        ]
    
    # Public utility methods
    
    def get_nat_statistics(self) -> Dict[str, Any]:
        """
        Get NAT statistics and session information.
        
        Returns:
            dict: NAT statistics
        """
        try:
            # This would implement actual NAT statistics retrieval from VPP
            # For now, return basic information
            return {
                'active_policies': len(self.active_policies),
                'policies': list(self.active_policies.keys()),
                'total_ports_mapped': sum(
                    len(policy['wg_ports']) + len(policy['tcp_ports']) + len(policy['udp_ports'])
                    for policy in self.active_policies.values()
                )
            }
            
        except Exception as e:
            log.error(f"Error getting NAT statistics: {e}")
            return {'error': str(e)}
    
    def verify_nat_configuration(self, policy_name: str) -> Dict[str, Any]:
        """
        Verify that a NAT policy is correctly configured in VPP.
        
        Args:
            policy_name: Name of the policy to verify
            
        Returns:
            dict: Verification results
        """
        if policy_name not in self.active_policies:
            return {'verified': False, 'error': 'Policy not found'}
        
        try:
            policy = self.active_policies[policy_name]
            
            # Check if NAT interfaces are configured in VPP
            current_config = self.connection.client.get_configuration()
            
            nat_interfaces = [
                item.config
                for item in current_config.items
                if isinstance(item.config, models.Nat44InterfaceConfigurationItem)
                and item.config.name in [policy['lan_interface'], policy['wan_interface']]
            ]
            
            # Check port mappings
            all_ports = set(policy['wg_ports'] + policy['tcp_ports'] + policy['udp_ports'])
            port_mappings = [
                item.config
                for item in current_config.items
                if isinstance(item.config, models.IdentityMapping)
                and item.config.port in all_ports
            ]
            
            interfaces_ok = len(nat_interfaces) == 2
            ports_ok = len(port_mappings) >= len(all_ports)
            
            return {
                'verified': interfaces_ok and ports_ok,
                'interfaces_configured': interfaces_ok,
                'ports_configured': ports_ok,
                'interface_count': len(nat_interfaces),
                'port_mapping_count': len(port_mappings),
                'expected_ports': len(all_ports)
            }
            
        except Exception as e:
            log.error(f"Error verifying NAT configuration for '{policy_name}': {e}")
            return {'verified': False, 'error': str(e)}
    
    # Private helper methods
    
    def _dict_to_interface(self, interface_config: Dict[str, Any]) -> Interface:
        """Convert dictionary to Interface object."""
        # This assumes your Interface class can be constructed from a dict
        # Adjust based on your actual Interface implementation
        return Interface(
            interface_name=interface_config.get('interface_name'),
            ip_address=interface_config.get('ip_address'),
            prefix_len=interface_config.get('prefix_len')
        )
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _find_nat_interfaces_in_config(self, current_config, interface_names: List[str]) -> List:
        """Find NAT interface configurations in VPP config."""
        return [
            item.config
            for item in current_config.items
            if isinstance(item.config, models.Nat44InterfaceConfigurationItem)
            and item.config.name in interface_names
        ]
    
    def _find_port_mappings_in_config(self, current_config, ports: List[int]) -> List:
        """Find port mapping configurations in VPP config."""
        return [
            item.config
            for item in current_config.items
            if isinstance(item.config, models.IdentityMapping)
            and item.config.port in ports
        ]
