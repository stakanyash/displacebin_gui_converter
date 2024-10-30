import flet as ft
from ui import create_ui
from localization import lang

def main(page: ft.Page):
    create_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
