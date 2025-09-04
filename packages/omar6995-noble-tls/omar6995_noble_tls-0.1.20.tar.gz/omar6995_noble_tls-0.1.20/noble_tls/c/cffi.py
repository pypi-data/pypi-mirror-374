import asyncio
import os
import ctypes

from noble_tls.exceptions.exceptions import TLSClientException
import noble_tls.updater.file_fetch as file_fetch
download_if_necessary = file_fetch.download_if_necessary
from noble_tls.utils.asset import generate_asset_name, root_dir


async def check_and_download_dependencies():
    """
    Check if the dependencies folder is empty and download necessary files if it is.
    """
    root_directory = root_dir()
    dependencies_dir = f'{root_directory}/dependencies'
    # Ensure directory exists before listing to avoid FileNotFoundError in CI
    if not os.path.exists(dependencies_dir):
        os.makedirs(dependencies_dir, exist_ok=True)
    contains_anything = [file for file in os.listdir(dependencies_dir) if not file.startswith('.')]
    if len(contains_anything) == 0:
        print(">> Dependencies folder is empty. Downloading the latest TLS release...")
        await download_if_necessary()


def run_async_task(task):
    """
    Run an asynchronous task taking into account the current event loop.
    :param task: Coroutine to run.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(task)
    else:
        if loop.is_running():
            asyncio.ensure_future(task)
        else:
            loop.run_until_complete(task)


def load_asset(is_aws=False):
    """
    Load the asset and return its name, download if necessary.
    :param is_aws: If True, load asset from data directory instead of downloading
    :return: Name of the asset.
    """
    if is_aws:
        # Load from data directory for AWS usage
        data_dir = f'{root_dir()}/data'
        if not os.path.exists(data_dir):
            raise TLSClientException(f"Data directory {data_dir} does not exist for AWS usage.")
        
        # Find .so, .dll, or .dylib files in data directory
        available_files = [f for f in os.listdir(data_dir) if f.endswith(('.so', '.dll', '.dylib'))]
        if not available_files:
            raise TLSClientException(f"No compatible asset files found in {data_dir} for AWS usage.")
        
        # Use the first available file
        asset_name = available_files[0]
        asset_path = f'{data_dir}/{asset_name}'
        print(f">> Using AWS asset {asset_name} from data directory.")
        return asset_name, True  # Return tuple indicating AWS mode
    
    # Original logic for non-AWS usage
    # Check if dependencies folder exists; create it to maintain previous behavior
    dependencies_dir = f'{root_dir()}/dependencies'
    if not os.path.exists(dependencies_dir):
        os.makedirs(dependencies_dir, exist_ok=True)

    current_asset, current_version = file_fetch.read_version_info()
    if not current_asset or not current_version:
        run_async_task(check_and_download_dependencies())
        current_asset, current_version = file_fetch.read_version_info()
        print(f">> Downloaded asset {current_asset} for version {current_version}.")

    asset_name = generate_asset_name(version=current_version)
    asset_path = f'{dependencies_dir}/{asset_name}'
    if not os.path.exists(asset_path):
        raise TLSClientException(f"Unable to find asset {asset_name} for version {current_version}.")

    return asset_name, False  # Return tuple indicating non-AWS mode


def initialize_library(is_aws=False):
    """
    Initialize and return the library.
    :param is_aws: If True, load asset from data directory instead of downloading
    :return: Loaded library object.
    """
    try:
        asset_name, is_aws_mode = load_asset(is_aws)
        
        if is_aws_mode:
            # Load from data directory
            library_path = f"{root_dir()}/data/{asset_name}"
        else:
            # Load from dependencies directory (original behavior)
            library_path = f"{root_dir()}/dependencies/{asset_name}"
        
        library = ctypes.cdll.LoadLibrary(library_path)
        return library
    except TLSClientException as e:
        print(f">> Failed to load the TLS Client asset: {e}")
    except OSError as e:
        print(f">> Failed to load the library: {e}")
        if os.name == "darwin":
            print(">> If you're on macOS, you need to allow the library to be loaded in System Preferences > Security & Privacy > General.")

        exit(1)


# Global variables to store library and functions
_library = None
_request_func = None
_free_memory_func = None

def detect_aws_mode() -> bool:
    """
    Detect whether the current runtime environment appears to be AWS Lambda or
    a restricted environment based on environment variables.

    Parameters:
        None

    Returns:
        bool: True if the environment suggests AWS/restricted mode; False otherwise.
    """
    if os.environ.get("NOBLE_TLS_AWS"):
        return True
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return True
    exec_env = os.environ.get("AWS_EXECUTION_ENV", "")
    if exec_env.startswith("AWS_Lambda"):
        return True
    return False

def get_library(is_aws=False):
    """
    Get the initialized library, initializing it if necessary.
    :param is_aws: If True, load asset from data directory instead of downloading
    :return: Loaded library object.
    """
    global _library, _request_func, _free_memory_func
    
    if _library is None or is_aws:
        _library = initialize_library(is_aws)
        
        # Define the request function from the shared package
        _request_func = _library.request
        _request_func.argtypes = [ctypes.c_char_p]
        _request_func.restype = ctypes.c_char_p

        _free_memory_func = _library.freeMemory
        _free_memory_func.argtypes = [ctypes.c_char_p]
        _free_memory_func.restype = ctypes.c_char_p
    
    return _library

def get_request_func(is_aws=False):
    """
    Get the request function, initializing library if necessary.
    :param is_aws: If True, load asset from data directory instead of downloading
    :return: Request function.
    """
    get_library(is_aws)
    return _request_func

def get_free_memory_func(is_aws=False):
    """
    Get the free memory function, initializing library if necessary.
    :param is_aws: If True, load asset from data directory instead of downloading
    :return: Free memory function.
    """
    get_library(is_aws)
    return _free_memory_func

# Backward compatibility shims (lazy initialization)
def request(payload: bytes) -> ctypes.c_char_p:
    """
    Backward-compatible request entrypoint.

    Parameters:
        payload (bytes): JSON-encoded request payload expected by the native library.

    Returns:
        ctypes.c_char_p: Pointer to a C string with the JSON-encoded response.
    """
    return get_request_func(detect_aws_mode())(payload)


def free_memory(pointer_id: bytes) -> ctypes.c_char_p:
    """
    Backward-compatible freeMemory entrypoint.

    Parameters:
        pointer_id (bytes): Identifier of the allocated memory returned by the native library.

    Returns:
        ctypes.c_char_p: Return value from the native freeMemory call.
    """
    return get_free_memory_func(detect_aws_mode())(pointer_id)
