import importlib.resources

def get_asset_path(filename):
    with importlib.resources.path('src_assets', filename) as path:
        return path
