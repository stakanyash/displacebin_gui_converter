import flet as ft
import sys
from ui import create_ui as create_main_ui
from reverse_ui import create_back_ui as create_reverse_ui
import logging

def main(page: ft.Page):
    if any(arg in sys.argv for arg in ("-reverse", "--reverse")):
        create_reverse_ui(page)
        logging.info("Launching reverse UI...")
    else:
        create_main_ui(page)
        logging.info("Launching main UI...")

ft.app(target=main, name="displace.bin GUI Converter")