import pytest
from unittest.mock import MagicMock, patch
from ..c.cffi import check_and_download_dependencies, run_async_task, load_asset, initialize_library


@pytest.mark.asyncio
async def test_check_and_download_dependencies_empty(mocker):
    mocker.patch('os.listdir', return_value=[])  # Mocking as if the dependencies directory is empty
    mocker.patch('noble_tls.c.cffi.download_if_necessary',
                 return_value=MagicMock())  # Mocking the download_if_necessary function
    await check_and_download_dependencies()  # No specific assertion, just checking it runs without error


@pytest.mark.asyncio
async def test_check_and_download_dependencies_not_empty(mocker):
    mocker.patch('os.listdir',
                 return_value=['file1', 'file2'])  # Mocking as if the dependencies directory contains files
    # No need to mock download_if_necessary as it should not be called
    await check_and_download_dependencies()  # No specific assertion, just checking it runs without error


def test_run_async_task(mocker):
    # Mock an asynchronous task
    async def async_task():
        return "Task completed"

    task = async_task()
    run_async_task(task)  # No specific assertion, just checking it runs without error


def test_load_asset(mocker):
    # Mock the os.path.exists function to simulate the dependency directory and file existence
    mocker.patch('os.path.exists', side_effect=[True, True])

    # Mock the read_version_info function to return a dummy asset name and version
    mocker.patch('noble_tls.updater.file_fetch.read_version_info', return_value=('some_asset', '1.0.0'))

    # Patch the generate_asset_name where it is used, which is in the c.ffi module
    mocker.patch('noble_tls.c.cffi.generate_asset_name', return_value='some_asset')

    # Call the load_asset function
    asset_name, is_aws_mode = load_asset()

    # Assert the returned asset name is 'some_asset' and not in AWS mode
    assert asset_name == 'some_asset', "Asset name should match the mocked value"
    assert is_aws_mode == False, "Should not be in AWS mode for normal usage"


def test_initialize_library(mocker):
    mocker.patch('noble_tls.c.cffi.load_asset', return_value=('some_asset', False))  # Mocking load_asset to return a tuple
    mocker.patch('ctypes.cdll.LoadLibrary',
                 return_value=MagicMock())  # Mocking LoadLibrary to return a MagicMock object
    library = initialize_library()
    assert library is not None, "Library should be initialized successfully"


def test_load_asset_aws_mode(mocker):
    # Mock the os.path.exists function to simulate the data directory existence
    mocker.patch('os.path.exists', return_value=True)
    
    # Mock os.listdir to return a list with a .so file
    mocker.patch('os.listdir', return_value=['tls-client-xgo-1.11.0-linux-amd64.so'])

    # Call the load_asset function with AWS mode
    asset_name, is_aws_mode = load_asset(is_aws=True)

    # Assert the returned asset name and AWS mode
    assert asset_name == 'tls-client-xgo-1.11.0-linux-amd64.so', "Asset name should match the available file"
    assert is_aws_mode == True, "Should be in AWS mode"


def test_initialize_library_aws_mode(mocker):
    mocker.patch('noble_tls.c.cffi.load_asset', return_value=('some_aws_asset.so', True))  # Mocking load_asset to return AWS tuple
    mocker.patch('ctypes.cdll.LoadLibrary',
                 return_value=MagicMock())  # Mocking LoadLibrary to return a MagicMock object
    library = initialize_library(is_aws=True)
    assert library is not None, "Library should be initialized successfully in AWS mode"