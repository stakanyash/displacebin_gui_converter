python -m nuitka --onefile main.py --include-module=localization --include-module=converter --include-module=ui --windows-icon-from-ico=".\assets\icon.ico" --windows-company-name="stakan" --windows-product-name="displace.bin converter" --windows-file-version=1.2 --windows-file-description="HTA map displace.bin file to raw/png GUI converter" --windows-console-mode=disable --include-data-dir=src_assets=src_assets