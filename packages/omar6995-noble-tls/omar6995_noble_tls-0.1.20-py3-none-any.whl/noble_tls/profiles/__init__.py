"""
Noble TLS Profiles Module

This module provides custom TLS profiles and identifiers for Noble TLS.
It includes functionality to load profiles from tls.peet.ws JSON files
and use them with custom client identifiers.
"""

# Import core profile functionality directly
try:
    # Try relative imports first (when used as a package)
    from .profiles import ProfileLoader, load_profile, list_profiles
    from .session_factory import create_session, list_all_identifiers
except ImportError:
    # Fall back to direct imports (when imported directly)
    from .profiles import ProfileLoader, load_profile, list_profiles
    from .session_factory import create_session, list_all_identifiers


def _lazy_import_custom_identifiers():
    """
    Lazy import function to avoid circular imports.
    
    Returns:
        tuple: CustomClient, CustomClientManager, custom_client_manager
    """
    try:
        from ..utils.custom_identifiers import CustomClient, CustomClientManager, get_custom_client_manager
        return CustomClient, CustomClientManager, get_custom_client_manager()
    except ImportError:
        from ..utils.custom_identifiers import CustomClient, CustomClientManager, get_custom_client_manager
        return CustomClient, CustomClientManager, get_custom_client_manager()


# For module-level access, use properties that lazy load
def __getattr__(name):
    """
    Dynamic attribute access for lazy loading of custom identifiers.
    
    Args:
        name (str): Attribute name
        
    Returns:
        Any: The requested attribute
        
    Raises:
        AttributeError: If attribute is not found
    """
    if name == 'CustomClient':
        CustomClient, _, _ = _lazy_import_custom_identifiers()
        return CustomClient
    elif name == 'CustomClientManager':
        _, CustomClientManager, _ = _lazy_import_custom_identifiers()
        return CustomClientManager
    elif name == 'custom_client_manager':
        _, _, custom_client_manager = _lazy_import_custom_identifiers()
        return custom_client_manager
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Core classes
    'ProfileLoader',
    'CustomClient', 
    'CustomClientManager',
    
    # Factory functions
    'create_session',
    
    # Convenience functions
    'load_profile',
    'list_profiles', 
    'list_all_identifiers',
    
    # Global instances
    'custom_client_manager'
]

# Version info
__version__ = "1.0.0"
__author__ = "Noble TLS Team"
__description__ = "Custom TLS profiles and identifiers for Noble TLS" 