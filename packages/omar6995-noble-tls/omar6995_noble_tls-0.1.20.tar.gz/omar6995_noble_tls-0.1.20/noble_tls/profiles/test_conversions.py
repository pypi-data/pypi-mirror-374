#!/usr/bin/env python3
"""
Test script to demonstrate the format conversions between tls.peet.ws and noble TLS.
This shows how the ProfileLoader converts the parameters to the correct format.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from profiles import ProfileLoader


def test_conversions():
    """
    Test the parameter conversions from tls.peet.ws format to noble TLS format.
    """
    print("Testing Parameter Conversions")
    print("=" * 50)
    
    # Create loader
    loader = ProfileLoader()
    
    # Test data from tls.peet.ws Chrome profile
    test_data = {
        "signature_algorithms": [
            "ecdsa_secp256r1_sha256",
            "rsa_pss_rsae_sha256", 
            "rsa_pkcs1_sha256",
            "ecdsa_secp384r1_sha384",
            "rsa_pss_rsae_sha384",
            "rsa_pkcs1_sha384",
            "rsa_pss_rsae_sha512",
            "rsa_pkcs1_sha512"
        ],
        "versions": ["TLS_GREASE (0x6a6a)", "TLS 1.3", "TLS 1.2"],
        "supported_groups": [
            "TLS_GREASE (0xcaca)",
            "X25519MLKEM768 (4588)",
            "X25519 (29)",
            "P-256 (23)",
            "P-384 (24)"
        ],
        "h2_settings": ["HEADER_TABLE_SIZE = 65536", "ENABLE_PUSH = 0", "INITIAL_WINDOW_SIZE = 6291456"]
    }
    
    print("1. Signature Algorithms Conversion:")
    print("   tls.peet.ws format → noble TLS format")
    for algo in test_data["signature_algorithms"]:
        converted = loader.SIGNATURE_ALGORITHM_MAP.get(algo, algo)
        print(f"   {algo} → {converted}")
    
    print("\n2. TLS Versions Conversion:")
    print("   tls.peet.ws format → noble TLS format")
    for version in test_data["versions"]:
        clean_version = version.split(" (")[0] if "(" in version else version
        converted = loader.VERSION_MAP.get(clean_version, clean_version)
        print(f"   {version} → {converted}")
    
    print("\n3. Key Share Curves Conversion:")
    print("   tls.peet.ws format → noble TLS format")
    for curve in test_data["supported_groups"]:
        clean_curve = curve.split(" (")[0] if "(" in curve else curve
        converted = loader.CURVE_MAP.get(clean_curve, clean_curve)
        print(f"   {curve} → {converted}")
    
    print("\n4. HTTP/2 Settings Conversion:")
    print("   tls.peet.ws format → noble TLS format")
    for setting in test_data["h2_settings"]:
        if " = " in setting:
            key, value = setting.split(" = ")
            converted_key = loader.H2_SETTINGS_MAP.get(key, key)
            print(f"   {key} = {value} → {converted_key} = {value}")
    
    print("\n5. Browser-Specific Header Orders:")
    print("   Available browser header orders:")
    for browser_type, headers in loader.browser_header_orders.items():
        print(f"   {browser_type.upper()}:")
        pseudo_headers = [h for h in headers if h.startswith(":")]
        regular_headers = [h for h in headers if not h.startswith(":")]
        print(f"     Pseudo headers: {pseudo_headers}")
        print(f"     Regular headers: {regular_headers[:5]}...")  # Show first 5
    
    print("\n6. Testing with actual Chrome profile (if available):")
    try:
        profiles = loader.list_available_profiles()
        if "chrome_137_windows" in profiles:
            session = loader.load_profile("chrome_137_windows")
            print("   ✓ Chrome profile loaded successfully")
            print(f"   Browser Type: {session['browser_type']}")
            print(f"   JA3: {session['ja3_string'][:50]}...")
            print(f"   Signature Algorithms: {session['supported_signature_algorithms']}")
            print(f"   Supported Versions: {session['supported_versions']}")
            print(f"   Key Share Curves: {session['key_share_curves']}")
            print(f"   H2 Settings: {session['h2_settings']}")
            print(f"   Pseudo Header Order: {session['pseudo_header_order']}")
            print(f"   Header Order: {session['header_order'][:8]}...")  # Show first 8
        else:
            print("   Chrome profile not found in data directory")
    except Exception as e:
        print(f"   Error loading profile: {e}")-+
    
    print("\n7. Browser Type vs Header Order Comparison:")
    # Test how different browser types would affect header ordering
    test_browser_types = ["chrome", "firefox", "safari", "edge"]
    
    for browser_type in test_browser_types:
        if browser_type in loader.browser_header_orders:
            pseudo_order = loader._extract_pseudo_header_order(browser_type)
            header_order = loader._extract_header_order(browser_type)
            print(f"   {browser_type.upper()}:")
            print(f"     Pseudo headers: {pseudo_order}")
            print(f"     Regular headers: {header_order[:6]}...")  # Show first 6


if __name__ == "__main__":
    test_conversions() 