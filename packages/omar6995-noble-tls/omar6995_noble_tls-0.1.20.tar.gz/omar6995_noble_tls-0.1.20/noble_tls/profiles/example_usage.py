#!/usr/bin/env python3
"""
Example usage of the ProfileLoader class.

This script demonstrates how to:
1. Load all available profiles
2. Load a specific profile 
3. Extract specific parameters from a profile
4. Use the convenience functions
"""

from profiles import ProfileLoader, load_profile, list_profiles


def main():
    """
    Demonstrate various ways to use the ProfileLoader.
    """
    print("ProfileLoader Example Usage")
    print("=" * 50)
    
    # Method 1: Using the ProfileLoader class directly
    print("1. Using ProfileLoader class:")
    loader = ProfileLoader()
    
    # List available profiles
    profiles = loader.list_available_profiles()
    print(f"   Available profiles: {profiles}")
    
    if profiles:
        # Load the first available profile
        profile_name = profiles[0]
        session = loader.load_profile(profile_name)
        
        print(f"   Loaded profile: {profile_name}")
        print(f"   JA3 String: {session['ja3_string']}")
        print(f"   User Agent: {session['user_agent'][:50]}...")
        print(f"   HTTP/2 Settings: {session['h2_settings']}")
        
    print()
    
    # Method 2: Using convenience functions
    print("2. Using convenience functions:")
    profiles = list_profiles()
    print(f"   Available profiles: {profiles}")
    
    if profiles:
        # Load specific profile using convenience function
        session = load_profile(profiles[0])
        print(f"   Loaded using convenience function: {profiles[0]}")
        print(f"   Supported Versions: {session['supported_versions']}")
        print(f"   Key Share Curves: {session['key_share_curves']}")
        
    print()
    
    # Method 3: Load all profiles at once
    print("3. Loading all profiles:")
    all_sessions = loader.load_all_profiles()
    
    for name, session in all_sessions.items():
        print(f"   Profile: {name}")
        print(f"     JA3 Hash: {session['ja3_hash']}")
        print(f"     TLS Version: {session['tls_version_negotiated']}")
        print(f"     Connection Flow: {session['connection_flow']}")
        print()
    
    # Method 4: Extract specific data you need
    print("4. Extracting specific TLS parameters:")
    if profiles:
        session = loader.load_profile(profiles[0])
        
        # Extract parameters for TLS configuration
        tls_config = {
            'ja3_string': session['ja3_string'],
            'supported_signature_algorithms': session['supported_signature_algorithms'],
            'supported_versions': session['supported_versions'],
            'key_share_curves': session['key_share_curves'],
            'cert_compression_algo': session['cert_compression_algo']
        }
        
        print("   TLS Configuration:")
        for key, value in tls_config.items():
            print(f"     {key}: {value}")
        
        print()
        
        # Extract HTTP/2 configuration
        h2_config = {
            'h2_settings': session['h2_settings'],
            'h2_settings_order': session['h2_settings_order'],
            'pseudo_header_order': session['pseudo_header_order'],
            'connection_flow': session['connection_flow'],
            'header_priority': session['header_priority']
        }
        
        print("   HTTP/2 Configuration:")
        for key, value in h2_config.items():
            print(f"     {key}: {value}")
    
    # Method 5: Demonstrate browser-specific header orders
    print("\n5. Browser-specific header orders:")
    print("   Demonstrating how different browser types affect header ordering:")
    
    # Show available browser types
    if loader.browser_header_orders:
        for browser_type, header_order in loader.browser_header_orders.items():
            print(f"   {browser_type.upper()}:")
            print(f"     Pseudo headers: {[h for h in header_order if h.startswith(':')]}")
            print(f"     Regular headers: {[h for h in header_order if not h.startswith(':')][:5]}...")  # Show first 5
            print()
    
    # Show how the profile uses the browser type
    if profiles:
        session = loader.load_profile(profiles[0])
        print(f"   Profile '{profiles[0]}' uses browser type: {session.get('browser_type', 'unknown')}")
        print(f"   Resulting pseudo header order: {session['pseudo_header_order']}")
        print(f"   Resulting header order: {session['header_order'][:10]}...")  # Show first 10


def create_noble_tls_session(profile_name: str):
    """
    Example function showing how to create a noble TLS session 
    with the extracted parameters.
    
    Args:
        profile_name (str): Name of the profile to load
        
    Returns:
        dict: Session configuration for noble TLS
    """
    # Load the profile
    session = load_profile(profile_name)
    
    # Create a session configuration that matches the format
    # mentioned in the user's requirements
    noble_session = {
        # JA3 fingerprint
        'ja3_string': session['ja3_string'],
        
        # HTTP/2 settings
        'h2_settings': session['h2_settings'],
        'h2_settings_order': session['h2_settings_order'],
        
        # TLS algorithms
        'supported_signature_algorithms': session['supported_signature_algorithms'],
        'supported_delegated_credentials_algorithms': session['supported_delegated_credentials_algorithms'],
        'supported_versions': session['supported_versions'],
        'key_share_curves': session['key_share_curves'],
        
        # Compression and encoding
        'cert_compression_algo': session['cert_compression_algo'],
        'additional_decode': session['additional_decode'],
        
        # HTTP/2 headers and flow
        'pseudo_header_order': session['pseudo_header_order'],
        'connection_flow': session['connection_flow'],
        'priority_frames': session['priority_frames'],
        'header_order': session['header_order'],
        'header_priority': session['header_priority'],
        
        # TLS extension settings
        'random_tls_extension_order': session['random_tls_extension_order']
    }
    
    return noble_session


if __name__ == "__main__":
    main()
    
    # Example of creating a noble TLS session
    print("\n" + "=" * 50)
    print("Creating Noble TLS Session Example:")
    
    profiles = list_profiles()
    if profiles:
        noble_session = create_noble_tls_session(profiles[0])
        print(f"Created session for profile: {profiles[0]}")
        print("Session ready for noble TLS usage!")
        
        # You would use noble_session with your TLS library here
        # Example: session = NobleTLS(**noble_session) 