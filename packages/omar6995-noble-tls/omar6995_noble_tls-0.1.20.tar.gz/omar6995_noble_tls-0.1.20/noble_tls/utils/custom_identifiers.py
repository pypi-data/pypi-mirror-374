#!/usr/bin/env python3
"""
Custom Client Identifiers for Noble TLS

This module provides custom client identifiers that automatically load
TLS profiles from the data directory. These identifiers work similarly
to the built-in Client enum but use custom profiles from tls.peet.ws.
"""

import os
import json
from enum import Enum
from typing import Dict, Optional, Any


class CustomClient(Enum):
    """
    Custom client identifiers that map to JSON profiles in the data directory.
    These identifiers automatically load the corresponding profile when used.
    """
    # Chrome profiles
    CHROME_137 = "chrome_137_macos"
    EDGE_137 = "edge_137_windows"
    SAFARI_18_3_IOS = "safari_18.3_ios"
    SAFARI_18_5_IOS = "safari_18.5_ios"
    # Add more custom profiles here as they become available
    # FIREFOX_132 = "firefox_132_windows"
    # SAFARI_18 = "safari_18_macos"
    # EDGE_131 = "edge_131_windows"


class CustomClientManager:
    """
    Manager class for handling custom client identifiers and their associated profiles.
    
    This class provides functionality to:
    - Load profiles associated with custom identifiers
    - Dynamically discover available profiles
    - Generate new custom identifiers
    - Convert custom identifiers to noble TLS session parameters
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the CustomClientManager.
        
        Args:
            data_dir (str): Path to the directory containing profile JSON files.
                          If None, uses the default 'data' directory.
        """
        self.data_dir = data_dir
        self.profile_loader = None
        self._custom_identifiers = {}
        # Delay initialization to avoid circular imports
        self._initialized = False
    
    def _get_profile_loader(self):
        """
        Lazy initialization of ProfileLoader to avoid circular imports.
        
        Returns:
            ProfileLoader: Instance of ProfileLoader
        """
        if self.profile_loader is None:
            # Import here to avoid circular dependency
            try:
                from ..profiles.profiles import ProfileLoader
            except ImportError:
                from profiles.profiles import ProfileLoader
            self.profile_loader = ProfileLoader(self.data_dir)
        return self.profile_loader
    
    def _ensure_initialized(self):
        """
        Ensure the manager is properly initialized.
        """
        if not self._initialized:
            self._load_custom_identifiers()
            self._initialized = True
    
    def _load_custom_identifiers(self) -> None:
        """
        Load custom identifiers from the CustomClient enum and available profiles.
        """
        # Load predefined custom identifiers
        for client in CustomClient:
            self._custom_identifiers[client.name] = client.value
        
        # Dynamically discover additional profiles
        try:
            profile_loader = self._get_profile_loader()
            available_profiles = profile_loader.list_available_profiles()
            
            for profile_name in available_profiles:
                # Generate identifier name from profile name
                identifier_name = self._generate_identifier_name(profile_name)
                
                # Only add if not already defined in CustomClient enum
                if identifier_name not in self._custom_identifiers:
                    self._custom_identifiers[identifier_name] = profile_name
        except Exception as e:
            # If we can't load profiles, just use the predefined ones
            print(f"Warning: Could not load dynamic profiles: {e}")
            print("This usually means the package data files were not installed correctly.")
            print("Available identifiers will be limited to predefined ones only.")
    
    def _generate_identifier_name(self, profile_name: str) -> str:
        """
        Generate an identifier name from a profile name.
        
        Args:
            profile_name (str): Name of the profile file (without .json)
            
        Returns:
            str: Generated identifier name
        """
        # Convert profile name to identifier format
        # Examples:
        # chrome_137_windows -> CHROME_137_WINDOWS
        # firefox_132_linux -> FIREFOX_132_LINUX
        # safari_18_macos -> SAFARI_18_MACOS
        
        return profile_name.upper()
    
    def get_available_identifiers(self) -> Dict[str, str]:
        """
        Get all available custom identifiers and their associated profile names.
        
        Returns:
            Dict[str, str]: Dictionary mapping identifier names to profile names
        """
        self._ensure_initialized()
        return self._custom_identifiers.copy()
    
    def is_custom_identifier(self, identifier_name: str) -> bool:
        """
        Check if an identifier is a custom identifier.
        
        Args:
            identifier_name (str): Name of the identifier to check
            
        Returns:
            bool: True if it's a custom identifier, False otherwise
        """
        self._ensure_initialized()
        return identifier_name in self._custom_identifiers
    
    def get_profile_name(self, identifier_name: str) -> Optional[str]:
        """
        Get the profile name associated with a custom identifier.
        
        Args:
            identifier_name (str): Name of the custom identifier
            
        Returns:
            Optional[str]: Profile name if found, None otherwise
        """
        self._ensure_initialized()
        return self._custom_identifiers.get(identifier_name)
    
    def load_profile_for_identifier(self, identifier_name: str) -> Optional[Dict[str, Any]]:
        """
        Load the profile associated with a custom identifier.
        
        Args:
            identifier_name (str): Name of the custom identifier
            
        Returns:
            Optional[Dict[str, Any]]: Loaded profile session dictionary, None if not found
        """
        self._ensure_initialized()
        profile_name = self.get_profile_name(identifier_name)
        if profile_name:
            try:
                profile_loader = self._get_profile_loader()
                return profile_loader.load_profile(profile_name)
            except Exception as e:
                print(f"Error loading profile for identifier {identifier_name}: {e}")
                return None
        return None
    
    def get_session_params_for_identifier(self, identifier_name: str) -> Optional[Dict[str, Any]]:
        """
        Get session parameters for a custom identifier that can be used with noble TLS Session.
        
        Args:
            identifier_name (str): Name of the custom identifier
            
        Returns:
            Optional[Dict[str, Any]]: Session parameters dictionary, None if not found
        """
        profile = self.load_profile_for_identifier(identifier_name)
        if profile:
            # Extract only the parameters needed for Session constructor
            session_params = {
                'client': None,  # Set to None to use custom TLS client
                'ja3_string': profile.get('ja3_string'),
                'h2_settings': profile.get('h2_settings'),
                'h2_settings_order': profile.get('h2_settings_order'),
                'supported_signature_algorithms': profile.get('supported_signature_algorithms'),
                'supported_delegated_credentials_algorithms': profile.get('supported_delegated_credentials_algorithms'),
                'supported_versions': profile.get('supported_versions'),
                'key_share_curves': profile.get('key_share_curves'),
                'cert_compression_algo': profile.get('cert_compression_algo'),
                'additional_decode': profile.get('additional_decode'),
                'pseudo_header_order': profile.get('pseudo_header_order'),
                'connection_flow': profile.get('connection_flow'),
                'priority_frames': profile.get('priority_frames'),
                'header_order': profile.get('header_order'),
                'header_priority': profile.get('header_priority'),
                'random_tls_extension_order': profile.get('random_tls_extension_order', False)
            }
            
            # Remove None values
            session_params = {k: v for k, v in session_params.items() if v is not None}
            
            return session_params
        return None
    
    def add_custom_identifier(self, identifier_name: str, profile_name: str) -> bool:
        """
        Add a new custom identifier manually.
        
        Args:
            identifier_name (str): Name for the new identifier
            profile_name (str): Name of the profile to associate with it
            
        Returns:
            bool: True if added successfully, False if profile doesn't exist
        """
        self._ensure_initialized()
        try:
            profile_loader = self._get_profile_loader()
            if profile_name in profile_loader.list_available_profiles():
                self._custom_identifiers[identifier_name] = profile_name
                return True
        except Exception:
            pass
        return False
    
    def print_available_identifiers(self) -> None:
        """
        Print all available custom identifiers in a formatted way.
        """
        self._ensure_initialized()
        print("Available Custom Client Identifiers:")
        print("=" * 50)
        
        for identifier_name, profile_name in self._custom_identifiers.items():
            try:
                profile_loader = self._get_profile_loader()
                profile_info = profile_loader.get_profile_info(profile_name)
                browser_type = profile_info.get('name', 'unknown').split('_')[0].title()
                print(f"{identifier_name:<25} -> {profile_name}")
                print(f"{'':>25}    Browser: {browser_type}")
                print(f"{'':>25}    JA3 Hash: {profile_info.get('ja3_hash', 'N/A')[:16]}...")
                print()
            except Exception:
                print(f"{identifier_name:<25} -> {profile_name} (profile load error)")


# Create a global instance with lazy initialization
_custom_client_manager = None

def get_custom_client_manager():
    """
    Get the global CustomClientManager instance, creating it if necessary.
    
    Returns:
        CustomClientManager: Global instance
    """
    global _custom_client_manager
    if _custom_client_manager is None:
        _custom_client_manager = CustomClientManager()
    return _custom_client_manager

# For backwards compatibility, create a module-level callable that acts like the instance
def _get_global_manager():
    """Get the global manager instance"""
    return get_custom_client_manager()

# Assign it to the module level for backwards compatibility
custom_client_manager = _get_global_manager()


def get_session_params(custom_client: CustomClient) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get session parameters for a CustomClient enum value.
    
    Args:
        custom_client (CustomClient): CustomClient enum value
        
    Returns:
        Optional[Dict[str, Any]]: Session parameters dictionary
    """
    return get_custom_client_manager().get_session_params_for_identifier(custom_client.name)


def list_custom_identifiers() -> Dict[str, str]:
    """
    Convenience function to list all available custom identifiers.
    
    Returns:
        Dict[str, str]: Dictionary mapping identifier names to profile names
    """
    return get_custom_client_manager().get_available_identifiers()


def is_custom_client(identifier_name: str) -> bool:
    """
    Check if a given identifier name is a custom client identifier.
    
    Args:
        identifier_name (str): Identifier name to check
        
    Returns:
        bool: True if it's a custom identifier
    """
    return get_custom_client_manager().is_custom_identifier(identifier_name)


# Example usage
if __name__ == "__main__":
    # Print available identifiers
    get_custom_client_manager().print_available_identifiers()
    
   