#!/usr/bin/env python3
"""
Example: Using Custom Client Identifiers with Noble TLS

This example demonstrates how to use the new custom client identifier system
to create sessions with profiles loaded from tls.peet.ws JSON files.
"""

import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.custom_identifiers import CustomClient, custom_client_manager
    from profiles.session_factory import create_session, list_all_identifiers
    from utils.identifiers import Client
    
    async def main():
        """
        Demonstrate various ways to use custom identifiers.
        """
        print("🚀 Noble TLS Custom Identifiers Example")
        print("=" * 60)
        
        # 1. Show all available identifiers
        print("1. Available Identifiers:")
        all_identifiers = list_all_identifiers()
        print(f"   Built-in: {len(all_identifiers['built_in'])} identifiers")
        print(f"   Custom:   {len(all_identifiers['custom'])} identifiers")
        print()
        
        # 2. List custom identifiers in detail
        print("2. Custom Client Identifiers:")
        custom_client_manager.print_available_identifiers()
        
        # 3. Create sessions using different methods
        print("\n3. Creating Sessions with Different Methods:")
        print("-" * 50)
        
        # Method A: Using CustomClient enum
        try:
            print("   Method A: Using CustomClient.CHROME_137")
            session_a = create_session(CustomClient.CHROME_137)
            print("   ✓ Session created successfully!")
            print(f"   Browser Type: {getattr(session_a, 'browser_type', 'N/A')}")
            print(f"   JA3: {session_a.ja3_string[:40] if session_a.ja3_string else 'N/A'}...")
            print(f"   H2 Settings: {list(session_a.h2_settings.keys()) if session_a.h2_settings else []}")
            print()
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print()
        
        # Method B: Using string identifier
        try:
            print("   Method B: Using string 'CHROME_137'")
            session_b = create_session("CHROME_137")
            print("   ✓ Session created successfully!")
            print(f"   Pseudo Headers: {session_b.pseudo_header_order}")
            print(f"   Header Order: {session_b.header_order[:6] if session_b.header_order else []}...")
            print()
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print()
        
        # Method C: Using built-in identifier for comparison
        try:
            print("   Method C: Using built-in Client.CHROME_131")
            session_c = create_session(Client.CHROME_131)
            print("   ✓ Session created successfully!")
            print(f"   Client ID: {session_c.client_identifier}")
            print(f"   Uses custom TLS: {session_c.client_identifier is None}")
            print()
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print()
        
        # 4. Make sample requests to demonstrate functionality
        print("4. Testing Custom Profile with Real Request:")
        print("-" * 50)
        
        try:
            # Create session with custom Chrome 137 profile
            session = create_session(CustomClient.CHROME_137)
            
            # Make a test request
            print("   Making test request to httpbin.org...")
            response = await session.get("https://httpbin.org/headers")
            
            if response.status_code == 200:
                print("   ✓ Request successful!")
                print(f"   Status: {response.status_code}")
                print(f"   Response size: {len(response.text)} bytes")
                
                # Check if the custom headers are being used
                response_data = response.json()
                headers = response_data.get('headers', {})
                user_agent = headers.get('User-Agent', '')
                
                print(f"   User-Agent sent: {user_agent[:50]}...")
                
                # Check for Chrome-specific headers
                chrome_headers = [h for h in headers.keys() if h.lower().startswith('sec-ch-')]
                if chrome_headers:
                    print(f"   Chrome headers detected: {chrome_headers}")
                else:
                    print("   No Chrome-specific headers found")
                    
            else:
                print(f"   ✗ Request failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Request error: {e}")
        
        print()
        
        # 5. Compare fingerprints
        print("5. Fingerprint Comparison:")
        print("-" * 50)
        
        try:
            # Get Chrome 137 custom profile
            chrome_137_params = custom_client_manager.get_session_params_for_identifier("CHROME_137")
            
            if chrome_137_params:
                print("   Chrome 137 Custom Profile:")
                print(f"   JA3: {chrome_137_params.get('ja3_string', 'N/A')}")
                print(f"   TLS Versions: {chrome_137_params.get('supported_versions', [])}")
                print(f"   Signature Algorithms: {len(chrome_137_params.get('supported_signature_algorithms', []))} algorithms")
                print(f"   Key Share Curves: {chrome_137_params.get('key_share_curves', [])}")
                print(f"   H2 Settings Order: {chrome_137_params.get('h2_settings_order', [])}")
                print()
                
                # Show the difference with built-in profile
                print("   Key Differences from Built-in Profiles:")
                print("   - Uses actual Chrome 137 TLS fingerprint from tls.peet.ws")
                print("   - Includes latest TLS extensions and cipher suites")
                print("   - Browser-specific header ordering")
                print("   - Accurate HTTP/2 settings")
                
        except Exception as e:
            print(f"   ✗ Error comparing fingerprints: {e}")
        
        print("\n" + "=" * 60)
        print("✨ Custom identifier example completed!")
        print("\nNext Steps:")
        print("1. Add more custom profiles to the /data directory")
        print("2. Update CustomClient enum with new identifiers")
        print("3. Use create_session() in your applications")
    
    def sync_example():
        """
        Synchronous example for cases where async is not needed.
        """
        print("🔧 Synchronous Custom Identifier Example")
        print("=" * 50)
        
        # Create session
        session = create_session(CustomClient.CHROME_137)
        print(f"✓ Session created with identifier: {CustomClient.CHROME_137.name}")
        print(f"Profile: {CustomClient.CHROME_137.value}")
        
        # Show session configuration
        print("\nSession Configuration:")
        print(f"JA3 String: {session.ja3_string[:50] if session.ja3_string else 'N/A'}...")
        print(f"H2 Settings: {session.h2_settings}")
        print(f"Supported Versions: {session.supported_versions}")
        print(f"Header Order: {session.header_order[:8] if session.header_order else []}...")
        
        # Add some custom headers for the session
        session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
        })
        
        print(f"\nSession ready for requests with {len(session.headers)} default headers")
        
        return session
    
    if __name__ == "__main__":
        # Run async example
        print("Running async example...")
        asyncio.run(main())
        
        print("\n" + "="*60 + "\n")
        
        # Run sync example
        print("Running sync example...")
        sync_example()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the noble-tls directory")
    print("and that all required modules are available.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 