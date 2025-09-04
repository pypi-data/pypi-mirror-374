import json
import os
import glob
from typing import Dict, List, Optional, Union, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfileLoader:
    """
    Custom profile loader class that loads TLS profiles from tls.peet.ws JSON files
    and converts them into noble TLS custom session dictionaries.
    
    This class extracts all necessary TLS fingerprinting parameters including JA3,
    HTTP/2 settings, supported algorithms, and other TLS/HTTP features needed
    for accurate browser fingerprint emulation.
    """
    
    # Conversion mappings from tls.peet.ws format to noble TLS format
    SIGNATURE_ALGORITHM_MAP = {
        # ECDSA algorithms
        "ecdsa_secp256r1_sha256": "ECDSAWithP256AndSHA256",
        "ecdsa_secp384r1_sha384": "ECDSAWithP384AndSHA384", 
        "ecdsa_secp521r1_sha512": "ECDSAWithP521AndSHA512",
        "ecdsa_sha1": "ECDSAWithSHA1",
        
        # RSA PSS algorithms
        "rsa_pss_rsae_sha256": "804",
        "rsa_pss_rsae_sha384": "805",
        "rsa_pss_rsae_sha512": "806",
        
        "rsa_pss_pss_sha256": "809",
        "rsa_pss_pss_sha384": "80a",
        "rsa_pss_pss_sha512": "80b",
        
        # RSA PKCS1 algorithms
        "rsa_pkcs1_sha256": "PKCS1WithSHA256",
        "rsa_pkcs1_sha384": "PKCS1WithSHA384", 
        "rsa_pkcs1_sha512": "PKCS1WithSHA512",
        "rsa_pkcs1_sha1": "PKCS1WithSHA1",
        
        # Ed25519
        "ed25519": "Ed25519",
        
        # SHA224 algorithms
        "rsa_pkcs1_sha224": "SHA224_RSA",
        "ecdsa_sha224": "SHA224_ECDSA"
    }
    
    VERSION_MAP = {
        "TLS_GREASE": "GREASE",
        "TLS 1.3": "1.3",
        "TLS 1.2": "1.2", 
        "TLS 1.1": "1.1",
        "TLS 1.0": "1.0"
    }
    
    CURVE_MAP = {
        "TLS_GREASE": "GREASE",
        "P-256": "P256",
        "P-384": "P384", 
        "P-521": "P521",
        "X25519": "X25519",
        "X25519MLKEM768": "X25519MLKEM768",
        "P256Kyber768": "P256Kyber768",
        "X25519Kyber512D": "X25519Kyber512D",
        "X25519Kyber768": "X25519Kyber768",
        "X25519Kyber768Old": "X25519Kyber768Old"
    }
    
    H2_SETTINGS_MAP = {
        "HEADER_TABLE_SIZE": "HEADER_TABLE_SIZE",
        "ENABLE_PUSH": "ENABLE_PUSH",
        "MAX_CONCURRENT_STREAMS": "MAX_CONCURRENT_STREAMS", 
        "INITIAL_WINDOW_SIZE": "INITIAL_WINDOW_SIZE",
        "MAX_FRAME_SIZE": "MAX_FRAME_SIZE",
        "MAX_HEADER_LIST_SIZE": "MAX_HEADER_LIST_SIZE",
        "NO_RFC7540_PRIORITIES" : 'UNKNOWN_SETTING_9',
        "UNKNOWN_SETTING_8" : 'UNKNOWN_SETTING_8',
        "UNKNOWN_SETTING_7" : 'UNKNOWN_SETTING_7'
    }
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the ProfileLoader.
        
        Args:
            data_dir (str): Path to the directory containing profile JSON files.
                          If None, uses the default 'data' directory relative to this file.
        """
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        else:
            self.data_dir = data_dir
        
        self.profiles = {}
        self.browser_header_orders = {}
        self._load_browser_header_orders()
        self._load_all_profiles()
    
    def _load_browser_header_orders(self) -> None:
        """
        Load browser header orders from the static JSON file.
        """
        header_orders_file = os.path.join(os.path.dirname(__file__), "browser_header_orders.json")
        
        try:
            with open(header_orders_file, 'r', encoding='utf-8') as f:
                self.browser_header_orders = json.load(f)
                logger.info(f"Loaded browser header orders for: {list(self.browser_header_orders.keys())}")
        except Exception as e:
            logger.error(f"Failed to load browser header orders from {header_orders_file}: {str(e)}")
            # Set default empty dict if loading fails
            self.browser_header_orders = {}
    
    def _load_all_profiles(self) -> None:
        """
        Load all JSON profile files from the data directory.
        """
        if not os.path.exists(self.data_dir):
            logger.error(f"Data directory does not exist: {self.data_dir}")
            logger.error("This usually means the package was not installed with data files included.")
            logger.error("Try reinstalling the package or check the installation method.")
            return
            
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        
        if not json_files:
            logger.warning(f"No JSON profile files found in {self.data_dir}")
            logger.warning("This usually means the package data files were not installed correctly.")
            return
        
        for json_file in json_files:
            try:
                profile_name = os.path.splitext(os.path.basename(json_file))[0]
                with open(json_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    self.profiles[profile_name] = profile_data
                    logger.info(f"Loaded profile: {profile_name}")
            except Exception as e:
                logger.error(f"Failed to load profile {json_file}: {str(e)}")
    
    def _extract_ja3_string(self, tls_data: Dict) -> str:
        """
        Extract JA3 string from TLS data.
        
        Args:
            tls_data (Dict): TLS section from the profile JSON
            
        Returns:
            str: JA3 string (TLSVersion, Ciphers, Extensions, EllipticCurves, EllipticCurvePointFormats)
        """
        return tls_data.get("ja3", "")
    
    def _extract_h2_settings(self, http2_data: Dict) -> Dict[str, int]:
        """
        Extract HTTP/2 settings from the profile data and convert to noble TLS format.
        
        Args:
            http2_data (Dict): HTTP/2 section from the profile JSON
            
        Returns:
            Dict[str, int]: HTTP/2 settings dictionary with noble TLS compatible keys
        """
        h2_settings = {}
        
        # Find SETTINGS frame in sent_frames
        for frame in http2_data.get("sent_frames", []):
            if frame.get("frame_type") == "SETTINGS":
                for setting in frame.get("settings", []):
                    # Parse settings like "HEADER_TABLE_SIZE = 65536"
                    if " = " in setting:
                        key, value = setting.split(" = ")
                        # Convert to noble TLS format
                        if key in self.H2_SETTINGS_MAP:
                            noble_key = self.H2_SETTINGS_MAP[key]
                        else:
                            logger.warning(f"Unknown HTTP/2 setting encountered: '{key}'. This may cause issues with HTTP/2 fingerprinting.")
                            noble_key = key
                        h2_settings[noble_key] = int(value)
        
        return h2_settings
    
    def _extract_h2_settings_order(self, http2_data: Dict) -> List[str]:
        """
        Extract HTTP/2 settings order from the profile data and convert to noble TLS format.
        
        Args:
            http2_data (Dict): HTTP/2 section from the profile JSON
            
        Returns:
            List[str]: List of HTTP/2 settings in noble TLS format and order
        """
        settings_order = []
        
        # Find SETTINGS frame in sent_frames
        for frame in http2_data.get("sent_frames", []):
            if frame.get("frame_type") == "SETTINGS":
                for setting in frame.get("settings", []):
                    # Parse settings like "HEADER_TABLE_SIZE = 65536"
                    if " = " in setting:
                        key, _ = setting.split(" = ")
                        # Convert to noble TLS format
                        if key in self.H2_SETTINGS_MAP:
                            noble_key = self.H2_SETTINGS_MAP[key]
                        else:
                            logger.warning(f"Unknown HTTP/2 setting encountered: '{key}'. This may cause issues with HTTP/2 fingerprinting.")
                            noble_key = key
                        settings_order.append(noble_key)
        
        return settings_order
    
    def _extract_signature_algorithms(self, tls_data: Dict) -> List[str]:
        """
        Extract supported signature algorithms from TLS extensions and convert to noble TLS format.
        
        Args:
            tls_data (Dict): TLS section from the profile JSON
            
        Returns:
            List[str]: List of supported signature algorithms in noble TLS format
        """
        for ext in tls_data.get("extensions", []):
            if ext.get("name") == "signature_algorithms (13)":
                peet_algorithms = ext.get("signature_algorithms", [])
                # Convert to noble TLS format
                noble_algorithms = []
                for algo in peet_algorithms:
                    # If it's a hex value, strip 0x prefix and pass through directly
                    if algo.startswith("0x"):
                        # Remove 0x prefix and pass the hex value
                        hex_value = algo[2:]
                        noble_algorithms.append(hex_value)
                    elif len(algo) <= 4 and all(c in "0123456789abcdefABCDEF" for c in algo):
                        # Already a hex value without 0x prefix
                        noble_algorithms.append(algo)
                    elif algo in self.SIGNATURE_ALGORITHM_MAP:
                        # Map known string names
                        noble_algo = self.SIGNATURE_ALGORITHM_MAP[algo]
                        noble_algorithms.append(noble_algo)
                    else:
                        # Unknown value that's neither hex nor in our mapping
                        logger.warning(f"Unknown signature algorithm encountered: '{algo}'. This may cause issues with TLS fingerprinting.")
                        # Still add it in case the API can handle it
                        noble_algorithms.append(algo)
                return noble_algorithms
        return []
    
    def _extract_supported_versions(self, tls_data: Dict) -> List[str]:
        """
        Extract supported TLS versions from extensions and convert to noble TLS format.
        
        Args:
            tls_data (Dict): TLS section from the profile JSON
            
        Returns:
            List[str]: List of supported TLS versions in noble TLS format
        """
        for ext in tls_data.get("extensions", []):
            if ext.get("name") == "supported_versions (43)":
                peet_versions = ext.get("versions", [])
                # Convert to noble TLS format
                noble_versions = []
                for version in peet_versions:
                    # Handle versions with hex codes like "TLS_GREASE (0x6a6a)"
                    if "(" in version:
                        clean_version = version.split(" (")[0]
                    else:
                        clean_version = version
                    
                    # If it's a hex value, strip 0x prefix and pass through directly
                    if clean_version.startswith("0x"):
                        # Remove 0x prefix and pass the hex value
                        hex_value = clean_version[2:]
                        noble_versions.append(hex_value)
                    elif len(clean_version) <= 4 and all(c in "0123456789abcdefABCDEF" for c in clean_version):
                        # Already a hex value without 0x prefix
                        noble_versions.append(clean_version)
                    elif clean_version in self.VERSION_MAP:
                        # Map known version names
                        noble_version = self.VERSION_MAP[clean_version]
                        noble_versions.append(noble_version)
                    else:
                        # Unknown version that's neither hex nor in our mapping
                        logger.warning(f"Unknown TLS version encountered: '{clean_version}'. This may cause issues with TLS fingerprinting.")
                        # Still add it in case the API can handle it
                        noble_versions.append(clean_version)
                return noble_versions
        return []
    
    def _extract_key_share_curves(self, tls_data: Dict) -> List[str]:
        """
        Extract key share curves from TLS extensions and convert to noble TLS format.
        
        Args:
            tls_data (Dict): TLS section from the profile JSON
            
        Returns:
            List[str]: List of key share curves in noble TLS format
        """
        key_share_curves = []
        
        # Extract from key_share extension (not supported_groups)
        for ext in tls_data.get("extensions", []):
            if ext.get("name") == "key_share (51)":
                shared_keys = ext.get("shared_keys", [])
                for key_dict in shared_keys:
                    # Each shared_keys entry is a dict with curve name as key
                    for curve_name_with_code in key_dict.keys():
                        # Convert format from "X25519 (29)" to "X25519"
                        if "(" in curve_name_with_code:
                            curve_name = curve_name_with_code.split(" (")[0]
                        else:
                            curve_name = curve_name_with_code
                        
                        # If it's a hex value, strip 0x prefix and pass through directly
                        if curve_name.startswith("0x"):
                            # Remove 0x prefix and pass the hex value
                            hex_value = curve_name[2:]
                            key_share_curves.append(hex_value)
                        elif len(curve_name) <= 4 and all(c in "0123456789abcdefABCDEF" for c in curve_name):
                            # Already a hex value without 0x prefix
                            key_share_curves.append(curve_name)
                        elif curve_name in self.CURVE_MAP:
                            # Map known curve names
                            noble_curve = self.CURVE_MAP[curve_name]
                            key_share_curves.append(noble_curve)
                        else:
                            # Unknown curve that's neither hex nor in our mapping
                            logger.warning(f"Unknown curve encountered: '{curve_name}'. This may cause issues with TLS fingerprinting.")
                            # Still add it in case the API can handle it
                            key_share_curves.append(curve_name)
        
        return key_share_curves
    
    def _extract_cert_compression_algo(self, tls_data: Dict) -> Optional[str]:
        """
        Extract certificate compression algorithm from TLS extensions.
        
        Args:
            tls_data (Dict): TLS section from the profile JSON
            
        Returns:
            Optional[str]: Certificate compression algorithm or None
        """
        for ext in tls_data.get("extensions", []):
            if ext.get("name") == "compress_certificate (27)":
                algorithms = ext.get("algorithms", [])
                if algorithms:
                    # Extract algorithm name from format like "brotli (2)"
                    algo = algorithms[0]
                    if "(" in algo:
                        return algo.split(" (")[0]
                    return algo
        return None
    
    def _extract_pseudo_header_order(self, browser_type: str) -> List[str]:
        """
        Extract pseudo header order based on browser type from static configuration.
        
        Args:
            browser_type (str): Type of browser (chrome, firefox, safari, etc.)
            
        Returns:
            List[str]: List of pseudo headers in order for the specified browser
        """
        # Get the full header order for the browser type
        browser_order = self.browser_header_orders.get(browser_type, [])
        
        # Extract only pseudo headers (those starting with ":")
        pseudo_header_order = [header for header in browser_order if header.startswith(":")]
        
        # If no browser-specific order found, return default order
        if not pseudo_header_order:
            pseudo_header_order = [":method", ":authority", ":scheme", ":path"]
            logger.warning(f"No header order found for browser type '{browser_type}', using default pseudo header order")
        
        return pseudo_header_order
    
    def _extract_connection_flow(self, http2_data: Dict) -> Optional[int]:
        """
        Extract connection flow / window size increment from HTTP/2 frames.
        
        Args:
            http2_data (Dict): HTTP/2 section from the profile JSON
            
        Returns:
            Optional[int]: Connection flow increment or None
        """
        # Find WINDOW_UPDATE frame in sent_frames
        for frame in http2_data.get("sent_frames", []):
            if frame.get("frame_type") == "WINDOW_UPDATE":
                return frame.get("increment")
        return None
    
    def _extract_header_priority(self, http2_data: Dict) -> Optional[Dict]:
        """
        Extract header priority from HTTP/2 HEADERS frame.
        
        Args:
            http2_data (Dict): HTTP/2 section from the profile JSON
            
        Returns:
            Optional[Dict]: Header priority settings or None
        """
        # Find HEADERS frame in sent_frames
        for frame in http2_data.get("sent_frames", []):
            if frame.get("frame_type") == "HEADERS" and "priority" in frame:
                priority = frame["priority"]
                # Clamp weight to uint8 range (0-255)
                weight = priority.get("weight", 256)
                if weight > 255:
                    weight = 255
                elif weight < 0:
                    weight = 0
                    
                return {
                    "streamDep": priority.get("depends_on", 0),
                    "exclusive": bool(priority.get("exclusive", False)),
                    "weight": weight
                }
        return None
    
    def _extract_header_order(self, browser_type: str) -> List[str]:
        """
        Extract header order based on browser type from static configuration (non-pseudo headers).
        
        Args:
            browser_type (str): Type of browser (chrome, firefox, safari, etc.)
            
        Returns:
            List[str]: List of header names in order for the specified browser
        """
        # Get the full header order for the browser type
        browser_order = self.browser_header_orders.get(browser_type, [])
        
        # Extract only non-pseudo headers (those not starting with ":")
        header_order = [header for header in browser_order if not header.startswith(":")]
        
        # If no browser-specific order found, return default order
        if not header_order:
            header_order = ["user-agent", "accept", "accept-encoding", "accept-language"]
            logger.warning(f"No header order found for browser type '{browser_type}', using default header order")
        
        return header_order
    
    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Load and convert a specific profile to noble TLS session format.
        
        Args:
            profile_name (str): Name of the profile to load (without .json extension)
            
        Returns:
            Dict[str, Any]: Noble TLS session dictionary with all required parameters
            
        Raises:
            KeyError: If the profile name is not found
            ValueError: If the profile data is invalid
        """
        if profile_name not in self.profiles:
            raise KeyError(f"Profile '{profile_name}' not found. Available profiles: {list(self.profiles.keys())}")
        
        profile_data = self.profiles[profile_name]
        
        # Extract browser type from profile data
        browser_type = profile_data.get("type", "chrome")  # Default to chrome if type not specified
        
        # Extract random TLS extension order setting
        random_tls_extension_order = profile_data.get("random_tls_extension_order", False)
        
        # Extract data from different sections
        tls_peet_data = profile_data.get("tls.peet.ws", {})
        tls_data = tls_peet_data.get("tls", {})
        http2_data = tls_peet_data.get("http2", {})
        
        # Build noble TLS session dictionary
        session_dict = {
            # Basic profile info
            "profile_name": profile_name,
            "browser_type": browser_type,
            "user_agent": tls_peet_data.get("user_agent", ""),
            
            # JA3 fingerprint
            "ja3_string": self._extract_ja3_string(tls_data),
            
            # HTTP/2 settings
            "h2_settings": self._extract_h2_settings(http2_data),
            "h2_settings_order": self._extract_h2_settings_order(http2_data),
            
            # TLS algorithms and features
            "supported_signature_algorithms": self._extract_signature_algorithms(tls_data),
            "supported_versions": self._extract_supported_versions(tls_data),
            "key_share_curves": self._extract_key_share_curves(tls_data),
            
            # Certificate and encoding settings
            "cert_compression_algo": self._extract_cert_compression_algo(tls_data),
            "additional_decode": None,  # Not directly available, would need to be inferred
            
            # HTTP/2 header and flow settings (using browser type)
            "pseudo_header_order": self._extract_pseudo_header_order(browser_type),
            "connection_flow": self._extract_connection_flow(http2_data),
            "priority_frames": [],  # Would need additional parsing
            "header_order": self._extract_header_order(browser_type),
            "header_priority": self._extract_header_priority(http2_data),
            
            # TLS extension randomization
            "random_tls_extension_order": random_tls_extension_order,
            
            # Additional useful data
            "ja3_hash": tls_data.get("ja3_hash", ""),
            "ja4": tls_data.get("ja4", ""),
            "akamai_fingerprint": http2_data.get("akamai_fingerprint", ""),
            "tls_version_record": tls_data.get("tls_version_record", ""),
            "tls_version_negotiated": tls_data.get("tls_version_negotiated", "")
        }
       
        return session_dict
    
    def list_available_profiles(self) -> List[str]:
        """
        Get a list of all available profile names.
        
        Returns:
            List[str]: List of available profile names
        """
        return list(self.profiles.keys())
    
    def load_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all available profiles and convert them to noble TLS session format.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping profile names to session dictionaries
        """
        all_sessions = {}
        
        for profile_name in self.profiles.keys():
            try:
                all_sessions[profile_name] = self.load_profile(profile_name)
                logger.info(f"Converted profile: {profile_name}")
            except Exception as e:
                logger.error(f"Failed to convert profile {profile_name}: {str(e)}")
        
        return all_sessions
    
    def get_profile_info(self, profile_name: str) -> Dict[str, str]:
        """
        Get basic information about a profile without full conversion.
        
        Args:
            profile_name (str): Name of the profile
            
        Returns:
            Dict[str, str]: Basic profile information
            
        Raises:
            KeyError: If the profile name is not found
        """
        if profile_name not in self.profiles:
            raise KeyError(f"Profile '{profile_name}' not found")
        
        profile_data = self.profiles[profile_name]
        tls_peet_data = profile_data.get("tls.peet.ws", {})
        tls_data = tls_peet_data.get("tls", {})
        
        return {
            "name": profile_data.get("name", profile_name),
            "user_agent": tls_peet_data.get("user_agent", ""),
            "http_version": tls_peet_data.get("http_version", ""),
            "ja3_hash": tls_data.get("ja3_hash", ""),
            "ja4": tls_data.get("ja4", ""),
            "tls_version": tls_data.get("tls_version_negotiated", "")
        }


# Convenience function for easy usage
def load_profile(profile_name: str, data_dir: str = None) -> Dict[str, Any]:
    """
    Convenience function to load a single profile.
    
    Args:
        profile_name (str): Name of the profile to load
        data_dir (str): Path to the data directory (optional)
        
    Returns:
        Dict[str, Any]: Noble TLS session dictionary
    """
    loader = ProfileLoader(data_dir)
    return loader.load_profile(profile_name)


def list_profiles(data_dir: str = None) -> List[str]:
    """
    Convenience function to list available profiles.
    
    Args:
        data_dir (str): Path to the data directory (optional)
        
    Returns:
        List[str]: List of available profile names
    """
    loader = ProfileLoader(data_dir)
    return loader.list_available_profiles()


# Example usage
if __name__ == "__main__":
    # Create profile loader
    loader = ProfileLoader()
    
    # List available profiles
    profiles = loader.list_available_profiles()
    print(f"Available profiles: {profiles}")
    
    # Load a specific profile
    if profiles:
        profile_name = profiles[0]
        session = loader.load_profile(profile_name)
        print(f"\nLoaded profile '{profile_name}':")
        print(f"JA3: {session['ja3_string']}")
        print(f"User Agent: {session['user_agent']}")
        print(f"H2 Settings: {session['h2_settings']}")
