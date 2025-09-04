#!/usr/bin/env python3
"""
Session Factory for Noble TLS

This module provides factory functions to create Session instances using
either built-in Client identifiers or custom CustomClient identifiers.
"""

import json
from typing import Optional, Union, Any
import sys
import os

# Use try-except to handle both package and direct imports
try:
    # Try relative imports first (when used as a package)
    from ..sessions import Session
    from ..utils.identifiers import Client
except ImportError:
    # Fall back to direct imports (when imported directly)
    # Add the parent directory to the Python path to import noble_tls modules
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from sessions import Session
    from utils.identifiers import Client


def _get_custom_imports():
    """
    Lazy import function to avoid circular imports.
    
    Returns:
        tuple: CustomClient, custom_client_manager
    """
    try:
        from ..utils.custom_identifiers import CustomClient, get_custom_client_manager
        return CustomClient, get_custom_client_manager()
    except ImportError:
        from utils.custom_identifiers import CustomClient, get_custom_client_manager
        return CustomClient, get_custom_client_manager()


def create_session(
    client: Optional[Union[Client, "CustomClient", str]] = None,
    **kwargs: Any
) -> Session:
    """
    Create a Session instance using either built-in or custom client identifiers.
    
    Args:
        client: Client identifier - can be:
                - Client enum value (built-in identifiers like Client.CHROME_131)
                - CustomClient enum value (custom identifiers like CustomClient.CHROME_137)
                - String name of custom identifier (like "CHROME_137")
                - None for manual configuration
        **kwargs: Additional session parameters that override profile defaults:
                - random_tls_extension_order: bool - Override TLS extension randomization
                - force_http1: bool - Force HTTP/1.1 usage
                - debug_level: int - Set debug output level
                - ja3_string: str - Custom JA3 fingerprint
                - h2_settings: dict - HTTP/2 settings
                - And any other Session parameters
        
    Returns:
        Session: Configured Session instance
        
    Examples:
        # Using built-in identifier
        session = create_session(Client.CHROME_131)
        
        # Using custom identifier (enum)
        session = create_session(CustomClient.CHROME_137)
        
        # Using custom identifier with randomized TLS extensions
        session = create_session(CustomClient.CHROME_137, random_tls_extension_order=True)
        
        # Using custom identifier (string)
        session = create_session("CHROME_137")
        
        # Manual configuration
        session = create_session(ja3_string="...", h2_settings={...})
    """
    
    # Get custom imports when needed
    CustomClient, custom_client_manager = _get_custom_imports()
    
    # Handle custom client identifiers
    if isinstance(client, CustomClient):
        # Load parameters for custom client
        custom_params = custom_client_manager.get_session_params_for_identifier(client.name)
        if custom_params:
            # Merge custom parameters with any provided kwargs
            merged_params = {**custom_params, **kwargs}
           
            return Session(**merged_params)
        else:
            raise ValueError(f"Failed to load profile for custom client {client.name}")
    
    elif isinstance(client, str):
        # Check if it's a custom identifier name
        if custom_client_manager.is_custom_identifier(client):
            custom_params = custom_client_manager.get_session_params_for_identifier(client)
            if custom_params:
                merged_params = {**custom_params, **kwargs}
                
                return Session(**merged_params)
            else:
                raise ValueError(f"Failed to load profile for custom client {client}")
        else:
            raise ValueError(f"Unknown custom client identifier: {client}")
    
    elif isinstance(client, Client) or client is None:
        # Use built-in client identifier or manual configuration
        return Session(client=client, **kwargs)
    
    else:
        raise ValueError(f"Invalid client type: {type(client)}. Must be Client, CustomClient, string, or None")


def list_all_identifiers() -> dict:
    """
    List all available client identifiers (both built-in and custom).
    
    Returns:
        dict: Dictionary with 'built_in' and 'custom' lists
    """
    CustomClient, custom_client_manager = _get_custom_imports()
    
    built_in = [client.value for client in Client]
    custom = list(custom_client_manager.get_available_identifiers().keys())
    
    return {
        'built_in': built_in,
        'custom': custom
    }


def get_identifier_info(identifier: Union[Client, "CustomClient", str]) -> dict:
    """
    Get information about a specific identifier.
    
    Args:
        identifier: Client identifier to get info for
        
    Returns:
        dict: Information about the identifier
    """
    CustomClient, custom_client_manager = _get_custom_imports()
    
    if isinstance(identifier, CustomClient):
        profile_name = custom_client_manager.get_profile_name(identifier.name)
        if profile_name:
            profile_loader = custom_client_manager._get_profile_loader()
            profile_info = profile_loader.get_profile_info(profile_name)
            return {
                'type': 'custom',
                'identifier': identifier.name,
                'profile_name': profile_name,
                'profile_info': profile_info
            }
    
    elif isinstance(identifier, str):
        if custom_client_manager.is_custom_identifier(identifier):
            profile_name = custom_client_manager.get_profile_name(identifier)
            if profile_name:
                profile_loader = custom_client_manager._get_profile_loader()
                profile_info = profile_loader.get_profile_info(profile_name)
                return {
                    'type': 'custom',
                    'identifier': identifier,
                    'profile_name': profile_name,
                    'profile_info': profile_info
                }
    
    elif isinstance(identifier, Client):
        return {
            'type': 'built_in',
            'identifier': identifier.name,
            'value': identifier.value
        }
    
    return {'type': 'unknown', 'identifier': str(identifier)}


def demo_usage():
    """
    Demonstrate how to use the session factory with different identifier types.
    """
    CustomClient, custom_client_manager = _get_custom_imports()
    
    print("Noble TLS Session Factory Demo")
    print("=" * 50)
    
    # List all available identifiers
    all_identifiers = list_all_identifiers()
    print(f"Built-in identifiers: {len(all_identifiers['built_in'])}")
    print(f"Custom identifiers: {len(all_identifiers['custom'])}")
    print()
    
    # Show custom identifiers
    print("Available Custom Identifiers:")
    custom_client_manager.print_available_identifiers()
    
    # Example: Create session with custom identifier
    try:
        print("\nCreating session with CustomClient.CHROME_137:")
        session = create_session(CustomClient.CHROME_137)
        print("✓ Session created successfully!")
        print(f"JA3: {session.ja3_string[:50] if session.ja3_string else 'N/A'}...")
        print(f"H2 Settings: {session.h2_settings}")
        print(f"Header Order: {session.header_order[:5] if session.header_order else []}...")
        
    except Exception as e:
        print(f"✗ Error creating session: {e}")
    
    # Example: Create session with string identifier
    try:
        print("\nCreating session with string identifier 'CHROME_137':")
        session = create_session("CHROME_137")
        print("✓ Session created successfully!")
        print(f"Pseudo Header Order: {session.pseudo_header_order}")
        
    except Exception as e:
        print(f"✗ Error creating session: {e}")
    
    # Example: Create session with built-in identifier
    try:
        print("\nCreating session with built-in Client.CHROME_131:")
        session = create_session(Client.CHROME_131)
        print("✓ Session created successfully!")
        print(f"JA3: {session.ja3_string[:50] if session.ja3_string else 'N/A'}...")
        
    except Exception as e:
        print(f"✗ Error creating session: {e}")


if __name__ == "__main__":
    demo_usage() 