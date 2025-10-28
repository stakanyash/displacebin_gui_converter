import requests
import json
import os
from packaging import version
import logging

GITHUB_API_URL = "https://api.github.com/repos/stakanyash/displacebin_gui_converter/releases/latest"

class DownloadCancelled(Exception):
    pass

def check_for_updates(current_version):
    try:
        response = requests.get(GITHUB_API_URL)
        if response.status_code == 200:
            release_info = response.json()
            latest_version = release_info['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(current_version):
                return {
                    'update_available': True,
                    'version': latest_version,
                    'download_url': release_info['assets'][0]['browser_download_url'],
                    'description': release_info['body']
                }
        return {'update_available': False}
    except Exception as e:
        logging.error(f"Update check failed: {str(e)}")
        return {'update_available': False, 'error': str(e)}

def download_update(url, progress_callback=None):
    logging.info(f"Starting update download from {url}")
    response = requests.get(url, stream=True)
    total_size_mb = int(response.headers.get('content-length', 0)) / (1024 * 1024)
    block_size = 1024
    downloaded = 0
    cancelled = False
    
    save_path = os.path.join(os.getcwd(), "update.exe")
    logging.info(f"Update will be saved to {save_path}")
    
    def cancel_download():
        nonlocal cancelled
        cancelled = True
        logging.info("Download cancelled by user")
        raise DownloadCancelled("Download cancelled by user")
    
    try:
        with open(save_path, 'wb') as f:
            for data in response.iter_content(block_size):
                if cancelled:
                    break
                f.write(data)
                downloaded += len(data)
                if progress_callback:
                    current_mb = downloaded / (1024 * 1024)
                    progress = (downloaded / int(response.headers.get('content-length', 0))) * 100
                    progress_callback(progress, current_mb, total_size_mb, cancel_download)
        
        if cancelled:
            if os.path.exists(save_path):
                os.remove(save_path)
                logging.info(f"Cleaned up cancelled download file: {save_path}")
            return None
        
        logging.info(f"Update successfully downloaded: {save_path}")
        return save_path
    except Exception as e:
        logging.error(f"Error during download: {str(e)}")
        if os.path.exists(save_path):
            os.remove(save_path)
            logging.info(f"Cleaned up incomplete download file: {save_path}")
        raise
