import requests
import json
import os
from packaging import version
import logging
import hashlib
import tempfile
import shutil
from typing import Optional, Callable, Dict
from threading import Lock

GITHUB_API_URL = "https://api.github.com/repos/stakanyash/displacebin_gui_converter/releases/latest"
TIMEOUT = 30
MAX_RETRIES = 3
CHUNK_SIZE = 8192

class DownloadCancelled(Exception):
    pass

class UpdateError(Exception):
    pass

def check_for_updates(current_version: str) -> Dict:
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                GITHUB_API_URL, 
                timeout=TIMEOUT,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            response.raise_for_status()
            
            release_info = response.json()
            latest_version = release_info['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(current_version):
                exe_asset = None
                for asset in release_info.get('assets', []):
                    if asset['name'].lower().endswith('.exe'):
                        exe_asset = asset
                        break
                
                if not exe_asset:
                    logging.warning("No .exe file found in release assets")
                    return {'update_available': False, 'error': 'No executable found'}
                
                return {
                    'update_available': True,
                    'version': latest_version,
                    'download_url': exe_asset['browser_download_url'],
                    'description': release_info.get('body', ''),
                    'file_size': exe_asset.get('size', 0),
                    'checksum': release_info.get('body', '').split('SHA256:')[-1].strip()[:64] if 'SHA256:' in release_info.get('body', '') else None
                }
            
            return {'update_available': False}
            
        except requests.RequestException as e:
            logging.warning(f"Update check attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                logging.error(f"Update check failed after {MAX_RETRIES} attempts")
                return {'update_available': False, 'error': str(e)}
        except (KeyError, IndexError, ValueError) as e:
            logging.error(f"Invalid release data format: {str(e)}")
            return {'update_available': False, 'error': 'Invalid release format'}
    
    return {'update_available': False, 'error': 'Max retries reached'}

def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def download_update(
    url: str, 
    progress_callback: Optional[Callable] = None,
    expected_checksum: Optional[str] = None
) -> Optional[str]:
    logging.info(f"Starting update download from {url}")
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"update_temp_{os.getpid()}.exe")
    final_path = os.path.join(os.getcwd(), "update.exe")
    
    cancelled = False
    cancel_lock = Lock()
    
    def cancel_download():
        nonlocal cancelled
        with cancel_lock:
            cancelled = True
        logging.info("Download cancellation requested")
    
    def is_cancelled():
        with cancel_lock:
            return cancelled
    
    for attempt in range(MAX_RETRIES):
        try:
            if is_cancelled():
                raise DownloadCancelled("Download cancelled before start")
            
            response = requests.get(url, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                raise UpdateError("Content-Length header missing or zero")
            
            total_size_mb = total_size / (1024 * 1024)
            downloaded = 0
            
            logging.info(f"Downloading to temporary location: {temp_path}")
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if is_cancelled():
                        raise DownloadCancelled("Download cancelled by user")
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            current_mb = downloaded / (1024 * 1024)
                            progress = (downloaded / total_size) * 100
                            try:
                                progress_callback(progress, current_mb, total_size_mb, cancel_download)
                            except Exception as e:
                                logging.error(f"Progress callback error: {e}")
            
            actual_size = os.path.getsize(temp_path)
            if actual_size != total_size:
                raise UpdateError(f"Size mismatch: expected {total_size}, got {actual_size}")
            
            if expected_checksum:
                logging.info("Verifying file integrity...")
                actual_checksum = calculate_sha256(temp_path)
                if actual_checksum.lower() != expected_checksum.lower():
                    raise UpdateError(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
                logging.info("File integrity verified successfully")
            
            if os.path.exists(final_path):
                os.remove(final_path)
            shutil.move(temp_path, final_path)
            
            logging.info(f"Update successfully downloaded: {final_path}")
            return final_path
            
        except DownloadCancelled:
            logging.info("Download cancelled by user")
            _cleanup_file(temp_path)
            return None
            
        except (requests.RequestException, OSError) as e:
            logging.warning(f"Download attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}")
            _cleanup_file(temp_path)
            
            if attempt == MAX_RETRIES - 1:
                logging.error(f"Download failed after {MAX_RETRIES} attempts")
                raise UpdateError(f"Download failed: {str(e)}")
        
        except UpdateError as e:
            logging.error(str(e))
            _cleanup_file(temp_path)
            raise
            
        except Exception as e:
            logging.error(f"Unexpected error during download: {str(e)}")
            _cleanup_file(temp_path)
            raise UpdateError(f"Unexpected error: {str(e)}")
    
    return None

def _cleanup_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logging.warning(f"Failed to cleanup file {file_path}: {e}")