import flet as ft
from ui import create_ui

def main(page: ft.Page):
    create_ui(page)

ft.app(target=main)