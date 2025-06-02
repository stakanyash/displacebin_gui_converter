import importlib.resources
import logging

def get_asset_path(filename):
    with importlib.resources.path('src_assets', filename) as path:
        logging.info(f"Path for assets is: {path}")
        return path
