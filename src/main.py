import flet as ft
import sys
import logging
from screeninfo import get_monitors
from lang_manager import LanguageManager

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:
    tk = None
    messagebox = None

def check_min_resolution_or_exit(min_w=1280, min_h=720):
    try:
        monitor = get_monitors()[0]
        w, h = monitor.width, monitor.height
    except Exception:
        return

    if w < min_w or h < min_h:
        msg = f"Screen resolution {w}x{h} is below the minimum required {min_w}x{min_h}."
        if messagebox and tk:
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Resolution error", msg)
                root.destroy()
            except Exception:
                print(msg)
        else:
            print(msg)
        sys.exit(1)

from ui import create_ui as create_main_ui
from reverse_ui import create_back_ui as create_reverse_ui

def get_language_from_args(default_lang="En"):
    if "-lang" in sys.argv:
        idx = sys.argv.index("-lang") + 1
        if idx < len(sys.argv):
            code = sys.argv[idx]
            return code
    return default_lang

def main(page: ft.Page):
    lang_code = get_language_from_args()
    if any(arg in sys.argv for arg in ("-reverse", "--reverse")):
        create_reverse_ui(page)
        logging.info("Launching reverse UI...")
    else:
        create_main_ui(page, lang_code)
        logging.info(f"Launching main UI with language: {lang_code}")


if __name__ == "__main__":
    check_min_resolution_or_exit()
    ft.app(target=main, name="displace.bin GUI Converter", view=ft.FLET_APP)