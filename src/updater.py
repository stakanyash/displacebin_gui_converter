import requests
import json
import os
from packaging import version
import logging
import hashlib
import tempfile
import shutil
import re
from typing import Optional, Callable, Dict, Any
from threading import Lock, Event
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/repos/stakanyash/displacebin_gui_converter/releases/latest"
TIMEOUT = 30
MAX_RETRIES = 3
CHUNK_SIZE = 8192
ALLOWED_DOMAINS = ('github.com', 'objects.githubusercontent.com')

class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DownloadCancelled(Exception):
    pass

class UpdateError(Exception):
    pass

@dataclass
class UpdateInfo:
    update_available: bool
    version: Optional[str] = None
    download_url: Optional[str] = None
    description: Optional[str] = None
    file_size: int = 0
    checksum: Optional[str] = None
    release_date: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class UpdateDownloader:
    def __init__(self):
        self._cancelled = False
        self._lock = Lock()
        self._cancel_event = Event()
        self.status = DownloadStatus.PENDING
    
    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True
            self._cancel_event.set()
            self.status = DownloadStatus.CANCELLED
        logger.info("Download cancellation requested")
    
    def is_cancelled(self) -> bool:
        with self._lock:
            return self._cancelled
    
    def reset(self) -> None:
        with self._lock:
            self._cancelled = False
            self._cancel_event.clear()
            self.status = DownloadStatus.PENDING

@contextmanager
def safe_temp_file(suffix: str = '.exe', prefix: str = 'update_'):
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
        prefix=prefix
    )
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        yield temp_path
    finally:
        _cleanup_file(temp_path)

def _cleanup_file(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")

def extract_checksum(body: str) -> Optional[str]:
    if not body:
        return None
    
    pattern = r'SHA256:\s*([a-fA-F0-9]{64})'
    match = re.search(pattern, body, re.IGNORECASE)
    
    if match:
        return match.group(1).lower()
    
    pattern_alt = r'\b([a-fA-F0-9]{64})\b'
    match_alt = re.search(pattern_alt, body)
    
    if match_alt:
        logger.warning("Found potential checksum without SHA256: prefix")
        return match_alt.group(1).lower()
    
    return None

def is_github_url(url: str) -> bool:
    if not url:
        return False
    
    url_lower = url.lower()
    return any(url_lower.startswith(f'https://{domain}') for domain in ALLOWED_DOMAINS)

def calculate_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest().lower()
    except Exception as e:
        raise UpdateError(f"Failed to calculate checksum: {str(e)}")

def parse_version_safe(version_string: str) -> Optional[version.Version]:
    try:
        clean_version = version_string.lstrip('vV')
        return version.parse(clean_version)
    except Exception as e:
        logger.error(f"Failed to parse version '{version_string}': {e}")
        return None

def check_for_updates(current_version: str) -> UpdateInfo:
    current_ver = parse_version_safe(current_version)
    if not current_ver:
        return UpdateInfo(
            update_available=False,
            error=f"Invalid current version: {current_version}"
        )
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Checking for updates (attempt {attempt + 1}/{MAX_RETRIES})")
            
            response = requests.get(
                GITHUB_API_URL,
                timeout=TIMEOUT,
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'DisplaceBin-Updater'
                }
            )
            
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                logger.error(f"GitHub API rate limit exceeded. Remaining: {rate_limit_remaining}")
                return UpdateInfo(
                    update_available=False,
                    error="GitHub API rate limit exceeded. Please try again later."
                )
            
            response.raise_for_status()
            release_info = response.json()
            
            latest_version_str = release_info.get('tag_name', '').lstrip('vV')
            latest_ver = parse_version_safe(latest_version_str)
            
            if not latest_ver:
                logger.error(f"Invalid version in release: {release_info.get('tag_name')}")
                return UpdateInfo(
                    update_available=False,
                    error="Invalid version format in latest release"
                )
            
            if latest_ver <= current_ver:
                logger.info(f"No update needed. Current: {current_version}, Latest: {latest_version_str}")
                return UpdateInfo(update_available=False)

            exe_asset = None
            for asset in release_info.get('assets', []):
                if asset.get('name', '').lower().endswith('.exe'):
                    exe_asset = asset
                    break
            
            if not exe_asset:
                logger.warning("No .exe file found in release assets")
                return UpdateInfo(
                    update_available=False,
                    error="No executable found in release"
                )
            
            download_url = exe_asset.get('browser_download_url', '')
            if not is_github_url(download_url):
                logger.error(f"Suspicious download URL: {download_url}")
                return UpdateInfo(
                    update_available=False,
                    error="Invalid download URL"
                )
            
            body = release_info.get('body', '')
            checksum = extract_checksum(body)
            
            if not checksum:
                logger.warning("No checksum found in release notes")
            
            release_date = None
            published_at = release_info.get('published_at')
            if published_at:
                try:
                    release_date = datetime.fromisoformat(published_at.replace('Z', '+00:00')).isoformat()
                except Exception as e:
                    logger.warning(f"Failed to parse release date: {e}")
            
            logger.info(f"Update available: {current_version} -> {latest_version_str}")
            
            return UpdateInfo(
                update_available=True,
                version=latest_version_str,
                download_url=download_url,
                description=body,
                file_size=exe_asset.get('size', 0),
                checksum=checksum,
                release_date=release_date
            )
            
        except requests.RequestException as e:
            logger.warning(f"Update check attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}")
            
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Update check failed after {MAX_RETRIES} attempts")
                return UpdateInfo(
                    update_available=False,
                    error=f"Network error: {str(e)}"
                )
        
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Invalid release data format: {str(e)}")
            return UpdateInfo(
                update_available=False,
                error=f"Invalid release format: {str(e)}"
            )
    
    return UpdateInfo(
        update_available=False,
        error="Max retries reached"
    )

def atomic_file_replace(temp_path: str, final_path: str) -> None:
    backup_path = None
    
    try:
        if os.path.exists(final_path):
            backup_path = final_path + '.backup'
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            shutil.move(final_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        shutil.move(temp_path, final_path)
        logger.info(f"File replaced successfully: {final_path}")
        
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
            logger.debug("Backup removed")
            
    except Exception as e:
        if backup_path and os.path.exists(backup_path):
            try:
                if os.path.exists(final_path):
                    os.remove(final_path)
                shutil.move(backup_path, final_path)
                logger.info("Restored from backup after error")
            except Exception as restore_error:
                logger.error(f"Failed to restore from backup: {restore_error}")
        
        raise UpdateError(f"Failed to replace file: {str(e)}")

def download_update(
    url: str,
    downloader: UpdateDownloader,
    progress_callback: Optional[Callable[[float, float, float, Callable], None]] = None,
    expected_checksum: Optional[str] = None
) -> Optional[str]:
    logger.info(f"Starting update download from {url}")
    
    if not is_github_url(url):
        raise UpdateError(f"Invalid download URL: {url}")
    
    final_path = os.path.join(os.getcwd(), "update.exe")
    
    target_dir = os.path.dirname(final_path) or '.'
    if not os.access(target_dir, os.W_OK):
        raise UpdateError(f"No write permission in directory: {target_dir}")
    
    downloader.reset()
    
    for attempt in range(MAX_RETRIES):
        if downloader.is_cancelled():
            logger.info("Download cancelled before start")
            return None
        
        with safe_temp_file() as temp_path:
            try:
                logger.info(f"Download attempt {attempt + 1}/{MAX_RETRIES}")
                downloader.status = DownloadStatus.DOWNLOADING
                
                response = requests.get(url, stream=True, timeout=TIMEOUT)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                if total_size == 0:
                    raise UpdateError("Content-Length header missing or zero")
                
                total_size_mb = total_size / (1024 * 1024)
                downloaded = 0
                
                logger.info(f"Downloading {total_size_mb:.2f} MB to: {temp_path}")
                
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if downloader.is_cancelled():
                            raise DownloadCancelled("Download cancelled by user")
                        
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback:
                                try:
                                    current_mb = downloaded / (1024 * 1024)
                                    progress = (downloaded / total_size) * 100
                                    progress_callback(
                                        progress,
                                        current_mb,
                                        total_size_mb,
                                        downloader.cancel
                                    )
                                except Exception as e:
                                    logger.error(f"Progress callback error: {e}")
                
                actual_size = os.path.getsize(temp_path)
                if actual_size != total_size:
                    raise UpdateError(
                        f"Size mismatch: expected {total_size} bytes, got {actual_size} bytes"
                    )
                
                logger.info(f"Download completed: {actual_size} bytes")
                
                if expected_checksum:
                    downloader.status = DownloadStatus.VERIFYING
                    logger.info("Verifying file integrity...")
                    
                    actual_checksum = calculate_sha256(temp_path)
                    
                    if actual_checksum != expected_checksum.lower():
                        raise UpdateError(
                            f"Checksum mismatch:\n"
                            f"Expected: {expected_checksum}\n"
                            f"Got:      {actual_checksum}"
                        )
                    
                    logger.info("File integrity verified successfully")
                else:
                    logger.warning("Skipping checksum verification (no checksum provided)")
                
                atomic_file_replace(temp_path, final_path)
                
                downloader.status = DownloadStatus.COMPLETED
                logger.info(f"Update successfully downloaded and verified: {final_path}")
                
                return final_path
                
            except DownloadCancelled:
                logger.info("Download cancelled by user")
                downloader.status = DownloadStatus.CANCELLED
                return None
                
            except (requests.RequestException, OSError) as e:
                logger.warning(f"Download attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}")
                
                if attempt == MAX_RETRIES - 1:
                    downloader.status = DownloadStatus.FAILED
                    raise UpdateError(f"Download failed after {MAX_RETRIES} attempts: {str(e)}")
            
            except UpdateError:
                downloader.status = DownloadStatus.FAILED
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error during download: {str(e)}", exc_info=True)
                downloader.status = DownloadStatus.FAILED
                raise UpdateError(f"Unexpected error: {str(e)}")
    
    downloader.status = DownloadStatus.FAILED
    return None