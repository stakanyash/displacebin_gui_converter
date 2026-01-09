import flet as ft
import sys
import logging
import locale
from screeninfo import get_monitors
from lang_manager import LanguageManager
from localization import translations

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

def get_system_language():
    try:
        locale.setlocale(locale.LC_ALL, '')
        current_locale = locale.getlocale()[0]
        
        if current_locale:
            system_lang = current_locale[:2].lower()
            
            lang_code = system_lang.capitalize()
            
            if lang_code in translations:
                logging.info(f"Detected system language: {lang_code}")
                return lang_code
            else:
                logging.warning(f"System language '{lang_code}' not supported, using English")
                return "En"
        else:
            logging.warning("Could not detect system locale, using English")
            return "En"
            
    except Exception as e:
        logging.error(f"Error detecting system language: {e}, defaulting to English")
        return "En"

def get_language_from_args():
    if "-lang" in sys.argv:
        try:
            idx = sys.argv.index("-lang") + 1
            if idx < len(sys.argv):
                code = sys.argv[idx]
                if code in translations:
                    logging.info(f"Language set from args: {code}")
                    return code
                else:
                    logging.warning(f"Language '{code}' from args not found, using system language")
        except Exception as e:
            logging.error(f"Error parsing -lang argument: {e}")
    
    return get_system_language()

def main(page: ft.Page):
    lang_code = get_language_from_args()
    
    LanguageManager.set_language(lang_code)
    
    if any(arg in sys.argv for arg in ("-reverse", "--reverse")):
        logging.info(f"Launching reverse UI with language: {lang_code}")
        create_reverse_ui(page, lang_code)
    else:
        logging.info(f"Launching main UI with language: {lang_code}")
        create_main_ui(page, lang_code)


if __name__ == "__main__":
    check_min_resolution_or_exit()
    ft.app(target=main, name="displace.bin GUI Converter", view=ft.FLET_APP)