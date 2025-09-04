import asyncio
import os
from functools import wraps
from typing import Tuple

from noble_tls.utils.asset import generate_asset_name
from noble_tls.utils.asset import root_dir
from noble_tls.exceptions.exceptions import TLSClientException
import httpx

owner = 'bogdanfinn'
repo = 'tls-client'
url = f'https://api.github.com/repos/{owner}/{repo}/releases/latest'
root_directory = root_dir()
GITHUB_TOKEN = os.getenv("GH_TOKEN")


def auto_retry(retries: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt <= retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        print(f">> Failed after {attempt} attempts with error: {e} using token: {GITHUB_TOKEN}")
                        raise e
                    await asyncio.sleep(0.1)

        return wrapper

    return decorator


@auto_retry(retries=3)
async def get_latest_release() -> Tuple[str, list]:
    """
    Fetches the latest release from the GitHub API.

    :return: Latest release tag name, and a list of assets
    """
    # Make a GET request to the GitHub API
    async with httpx.AsyncClient() as client:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'noble-tls'
        }
        
        # Only add token if it exists and is not empty
        if GITHUB_TOKEN and GITHUB_TOKEN.strip():
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
            print(">> Using GitHub token for authentication in get_latest_release.")
        else:
            print(">> No GitHub token found, using unauthenticated requests (may hit rate limits)")
            
        response = await client.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse the JSON data from the response
        version_num = data['tag_name'].replace('v', '')  # Return the tag name without the 'v' prefix
        if 'assets' not in data:
            raise TLSClientException(f"Version {version_num} does not have any assets.")

        # Get assets
        assets = data['assets']
        return version_num, assets
    elif response.status_code == 403:
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
        rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'unknown')
        error_msg = f"GitHub API rate limit exceeded (403). Remaining: {rate_limit_remaining}, Reset: {rate_limit_reset}"
        if GITHUB_TOKEN:
            error_msg += f". Check if your GH_TOKEN has the correct permissions (needs 'repo' or 'public_repo' scope)."
        else:
            error_msg += ". Consider setting a GH_TOKEN environment variable to increase rate limits."
        raise TLSClientException(error_msg)
    else:
        raise TLSClientException(f"Failed to fetch the latest release. Status code: {response.status_code}, Response: {response.text}")


async def download_and_save_asset(
        asset_url: str,
        asset_name: str,
        version: str
) -> None:
    # Download
    async with httpx.AsyncClient(follow_redirects=True) as client:
        headers = {
            'Accept': 'application/octet-stream',
            'User-Agent': 'rawandahmad698',
            'Connection': 'keep-alive'
        }
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
            print(">> Using GitHub token for authentication.")

        response = await client.get(asset_url, headers=headers)
        if response.status_code != 200:
            raise TLSClientException(f"Failed to download asset {asset_name}. Status code: {response.status_code}")

        with open(f'{root_directory}/dependencies/{asset_name}', 'wb') as f:
            f.write(response.content)

        # Save version info
        await save_version_info(asset_name, version)


async def save_version_info(asset_name: str, version: str):
    """
    Save version info to a hidden .version file in root_dir/dependencies
    """
    with open(f'{root_directory}/dependencies/.version', 'w') as f:
        f.write(f"{asset_name} {version}")


def delete_version_info():
    """
    Delete everything inside dependencies/.version
    """
    try:
        # Delete all files in dependencies
        for file in os.listdir(f'{root_directory}/dependencies'):
            os.remove(f'{root_directory}/dependencies/{file}')
    except FileNotFoundError:
        pass


def read_version_info():
    """
    Read version info from a hidden .version file in root_dir/dependencies
    """
    try:
        with open(f'{root_directory}/dependencies/.version', 'r') as f:
            data = f.read()
            data = data.split(' ')
            return data[0], data[1]
    except FileNotFoundError:
        return None, None


async def download_if_necessary():
    """
    Download the TLS client asset if necessary.
    
    This function checks if the required TLS client library exists, and downloads it if not found.
    It automatically creates the dependencies directory if it doesn't exist.
    
    :raises TLSClientException: If the version has no assets or the required asset cannot be found
    """
    version_num, asset_url = await get_latest_release()
    if not asset_url or not version_num:
        raise TLSClientException(f"Version {version_num} does not have any assets.")

    # Ensure dependencies directory exists
    dependencies_dir = f'{root_directory}/dependencies'
    if not os.path.exists(dependencies_dir):
        os.makedirs(dependencies_dir)

    asset_name = generate_asset_name(custom_part=repo, version=version_num)
    # Check if asset name is in the list of assets in root dir/dependencies
    if os.path.exists(f'{dependencies_dir}/{asset_name}'):
        return

    download_url = [asset['browser_download_url'] for asset in asset_url if asset['name'] == asset_name]
    if len(download_url) == 0:
        raise TLSClientException(f"Unable to find asset {asset_name} for version {version_num}.")

    download_url = download_url[0]
    await download_and_save_asset(download_url, asset_name, version_num)


async def update_if_necessary():
    current_asset, current_version = read_version_info()
    if not current_asset or not current_version:
        raise TLSClientException("Unable to read version info, no TLS libs found, use download_if_necessary()")

    version_num, asset_url = await get_latest_release()
    if not asset_url or not version_num:
        raise TLSClientException(f"Version {version_num} does not have any assets.")

    if version_num != current_version:
        print(f">> Current version {current_version} is outdated, downloading the latest TLS release...")
        await download_if_necessary()


if __name__ == "__main__":
    asyncio.run(update_if_necessary())
