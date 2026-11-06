import sys
import logging
import locale
import ctypes

from lang_manager import LanguageManager
from localization import translations
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QFont, QFontDatabase, QSurfaceFormat
from ui_components import AppWindow, asset_path
from settings_manager import settings

from ui import create_ui as create_main_ui
from reverse_ui import create_back_ui as create_reverse_ui


def check_min_resolution_or_exit(app, min_w=1280, min_h=720):
    screen = app.primaryScreen()
    if not screen:
        return

    geometry = screen.availableGeometry()
    w, h = geometry.width(), geometry.height()

    if w < min_w or h < min_h:
        msg = f"Screen resolution {w}x{h} is below the minimum required {min_w}x{min_h}."
        logging.error(msg)
        QMessageBox.critical(None, "Resolution error", msg)
        sys.exit(1)


def get_system_language():
    try:
        locale.setlocale(locale.LC_ALL, "")
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
                    logging.warning(f"Language '{code}' from args not found, ignoring.")
        except Exception as e:
            logging.error(f"Error parsing -lang argument: {e}")

    return None


def main():

    if sys.platform == "win32":
        try:
            app_id = "stakanyash.displacebox.2.3"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception as e:
            logging.warning(f"Failed to set AppUserModelID: {e}")



    fmt = QSurfaceFormat()
    fmt.setSwapInterval(1)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)





    lang_code = get_language_from_args()
    if not lang_code:
        lang_code = settings.get("language")
    if not lang_code:
        lang_code = get_system_language()

    LanguageManager.set_language(lang_code)
    settings.set("language", lang_code)

    app = QApplication(sys.argv)
    app.setApplicationName("DisplaceBox")
    app.setWindowIcon(QIcon(asset_path("icon.ico")))

    check_min_resolution_or_exit(app)


    font_files = [
        "fonts/Inter_18pt-Regular.ttf",
        "fonts/Inter_18pt-Medium.ttf",
        "fonts/Inter_18pt-SemiBold.ttf",
        "fonts/Inter_18pt-Bold.ttf"
    ]

    for font_file in font_files:
        try:
            path = asset_path(font_file)
            font_id = QFontDatabase.addApplicationFont(path)
            if font_id == -1:
                logging.warning(f"Failed to load font: {font_file} (path: {path})")
            else:
                logging.info(f"Successfully loaded font: {font_file}")
        except Exception as e:
            logging.error(f"Error loading font {font_file}: {e}")

    default_font = QFont("Inter", 10)
    app.setFont(default_font)


    window = AppWindow()
    window.theme_mode = settings.get("theme", "dark")

    if any(arg in sys.argv for arg in ("-reverse", "--reverse")):
        logging.info(f"Launching reverse UI with language: {lang_code}")
        create_reverse_ui(window, lang_code)
    else:
        logging.info(f"Launching main UI with language: {lang_code}")
        create_main_ui(window, lang_code)

    window.show()
    frame = window.frameGeometry()
    screen = app.primaryScreen().availableGeometry().center()
    frame.moveCenter(screen)
    window.move(frame.topLeft())
    sys.exit(app.exec())


if __name__ == "__main__":
    main()