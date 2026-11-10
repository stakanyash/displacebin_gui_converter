from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QProgressBar, QTextEdit, QButtonGroup, QPushButton
)
from localization import translations
import os
from resources import get_asset_path
import logging
from datetime import datetime
import traceback
from updater import UpdateDownloader, check_for_updates, download_update
from converter import process_raw, process_png, struct
import subprocess
import time
from config import VERSION, BUILD, LOG_LEVEL
from ui_components import (
    UIComponents, ThemeManager, LanguageDialog, AppWindow, OutlinedLineEdit, OutlinedComboBox,
    PillButton, _wrap_text, make_card, dialog_title_row, material_icon, AnimatedRadioButton,
    ConversionThread
)
from lang_manager import LanguageManager
from settings_manager import settings

CHECKED_FOR_UPDATES = False

log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"dgc_{log_timestamp}.log"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)


class UpdateCheckThread(QThread):
    result = pyqtSignal(object)

    def __init__(self, version):
        super().__init__()
        self.version = version

    def run(self):
        try:
            self.result.emit(check_for_updates(self.version))
        except Exception as e:
            logging.error(f"Error checking for updates: {str(e)}")
            logging.error(traceback.format_exc())
            self.result.emit(None)


class DownloadThread(QThread):
    progress = pyqtSignal(float, float, float)
    succeeded = pyqtSignal(str)
    cancelled = pyqtSignal()
    failed = pyqtSignal(object)

    def __init__(self, url, downloader, checksum):
        super().__init__()
        self.url = url
        self.downloader = downloader
        self.checksum = checksum

    def run(self):
        from updater import DownloadCancelled, UpdateError
        try:
            save_path = download_update(
                self.url,
                self.downloader,
                lambda value, current_size, total_size, cancel_fn: self.progress.emit(value, current_size, total_size),
                self.checksum,
            )
            if save_path:
                self.succeeded.emit(save_path)
            else:
                self.cancelled.emit()
        except Exception as e:
            self.failed.emit(e)


def create_ui(window: AppWindow, lang_code="En"):
    global lang

    if lang_code is None:
        lang_code = LanguageManager.get_language()

    if lang_code in translations:
        lang = translations[lang_code]
    else:
        lang = translations["En"]

    window.window_title_text = "DisplaceBox"
    window.setWindowTitle("DisplaceBox")
    window.clear_ui()

    scale_factor = 1.0
    ui_components = UIComponents(window, lang, scale_factor)

    def switch_to_reverse_ui(_page=None):
        from reverse_ui import create_back_ui

        def do_switch():
            logging.info("Switched to \".raw/.png --> .bin\" mode")
            create_back_ui(window, LanguageManager.get_language())

        window.smooth_transition(do_switch)

    top_bar, minimize_btn, close_btn, topbarico = ui_components.create_top_bar()
    window.add_ui(top_bar)

    title_container, title_image = ui_components.create_title_container()
    window.add_ui(title_container)

    input_file_path = {"value": None}

    def try_autodetect_size(filepath):
        try:
            dir_path = os.path.dirname(filepath)
            map_name = os.path.basename(dir_path)
            parent_dir = os.path.dirname(dir_path)

            ssl_path = os.path.join(parent_dir, f"{map_name}.ssl")

            if not os.path.exists(ssl_path):
                raise FileNotFoundError("SSL file not found")

            import xml.etree.ElementTree as ET
            tree = ET.parse(ssl_path)
            root = tree.getroot()

            levelsize = None
            for key in root.findall(".//Key"):
                if key.get("name") == "LEVELSIZE":
                    levelsize = key.text.strip()
                    break

            if not levelsize:
                raise ValueError("LEVELSIZE not found in SSL")

            expected_text = f"{levelsize}x{levelsize}"

            for key, text in [("64", "4x4"), ("128", "8x8"), ("256", "16x16"), ("512", "32x32"), ("1024", "64x64")]:
                if text == expected_text:
                    output_size.set_current_key(key)
                    return

            raise ValueError(f"Unsupported level size: {levelsize}")

        except Exception as e:
            logging.warning(f"Auto-size detection failed: {e}")
            ui_components.show_colored_dialog(
                "#E65100",
                "warning",
                lang["warning"],
                lang.get("autosizedetect_error", "Failed to automatically determine map size. Please select it manually."),
                [("OK", None)]
            )

    def on_file_selected(path):
        try:
            if not path:
                logging.info("User closed file picker.")
                return False
            if not path.lower().endswith(".bin"):
                ui_components.show_error_dialog(lang["error"], lang["wrong_extension"])
                file_name.set_value("")
                input_file_path["value"] = None
                logging.error("Selected file is not .bin file!")
                return False
        except AttributeError:
            logging.info("User closed file picker.")
            return False

        input_file_path["value"] = path
        file_name.set_value(path)
        return True

    def select_file(_e=None):
        last_dir = settings.get("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(window, lang["sel_button"], last_dir, "BIN (*.bin);;All files (*.*)")
        if on_file_selected(path):
            settings.set("last_dir", os.path.dirname(path))
            try_autodetect_size(path)

    def helpdialog(_e=None):
        colors = ThemeManager.get_theme_colors(window.theme_mode)
        ui_components.show_themed_dialog(
            "info_outline",
            lang["help"],
            _wrap_text(lang["help_text"], colors["text_color"]),
            [("OK", None, None)],
            width=480,
        )

    file_name = OutlinedLineEdit(lang["select_file"], width=int(400 * scale_factor))

    select_button = PillButton(lang["sel_button"], hpad=int(20 * scale_factor), vpad=int(10 * scale_factor), font_size=int(14 * scale_factor))
    select_button.clicked.connect(select_file)

    output_format_text = QLabel(lang["select_format"])
    output_format_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
    font = QFont()
    font.setPointSize(11)
    output_format_text.setFont(font)

    radio_raw = AnimatedRadioButton(".raw")
    radio_png = AnimatedRadioButton(".png")
    format_group = QButtonGroup(window)
    format_group.setExclusive(True)
    format_group.addButton(radio_raw)
    format_group.addButton(radio_png)
    window._format_group = format_group

    def current_format():
        if radio_raw.isChecked():
            return "RAW"
        if radio_png.isChecked():
            return "PNG"
        return None

    output_size = OutlinedComboBox(
        lang["select_size"],
        [("64", "4x4"), ("128", "8x8"), ("256", "16x16"), ("512", "32x32"), ("1024", "64x64")],
        width=int(350 * scale_factor),
    )

    process_button = PillButton(lang["convert_file"], hpad=int(16 * scale_factor), vpad=int(6 * scale_factor), font_size=int(12 * scale_factor))

    def process_file(_e=None):
        fmt = current_format()
        size_key = output_size.current_key()
        if not (input_file_path["value"] and fmt and size_key):
            ui_components.show_colored_dialog(
                "#B71C1C",
                "warning",
                lang["error"],
                lang["plssel_file"],
                [("OK", None)],
            )
            logging.warning("File is not selected!")
            return

        try:
            size = int(size_key)
        except Exception:
            size = 64

        output_path = os.path.splitext(input_file_path["value"])[0] + (".raw" if fmt == "RAW" else ".png")

        process_button.setEnabled(False)
        window.show_loading_snackbar(lang.get("converting", "Converting..."))

        func = process_raw if fmt == "RAW" else process_png
        thread = ConversionThread(func, input_file_path["value"], output_path, size, True)
        window._conversion_thread = thread

        def on_success(result):
            _min, _max, _del, json_path = result

            extra = []
            extra.append(_wrap_text(f"{lang['file_saved']}:", "#FFFFFF", 14, bold=True))
            extra.append(_wrap_text(output_path, "#FFFFFF", 12))
            if json_path:
                extra.append(_wrap_text(f"{lang['meta_path']}", "#FFFFFF", 14, bold=True))
                extra.append(_wrap_text(json_path, "#FFFFFF", 12))

            def log_stats():
                logging.info(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}")

            def show_result():
                process_button.setEnabled(True)
                ui_components.show_colored_dialog(
                    "#0A8A3C",
                    "check",
                    lang["result"],
                    None,
                    [("OK", None)],
                    extra_widgets=extra,
                    on_dismiss=log_stats,
                )
                logging.info(f"Converted file saved to: {output_path}")

            window.hide_loading_snackbar(min_duration_ms=1200, on_finished=show_result)

        def on_fail(e):
            def show_error():
                process_button.setEnabled(True)

                if isinstance(e, struct.error):
                    ui_components.show_colored_dialog(
                        "#B71C1C",
                        "warning",
                        lang["error"],
                        lang["struct_error"],
                        [("OK", None)],
                    )
                    logging.error(f"struct.error occurred: {e}")
                elif isinstance(e, ZeroDivisionError):
                    ui_components.show_colored_dialog(
                        "#D50000",
                        "error",
                        lang["error"],
                        lang["zerodiv_error"],
                        [
                            ("OK", None),
                            (lang["opengit"], lambda: window.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new")),
                        ],
                    )
                    logging.error(f"ZeroDivisionError occurred: {e}")
                else:
                    ui_components.show_error_dialog(lang["error"], str(e))
                    logging.error(f"Unexpected error: {e}")

                logging.error("Traceback:\n" + traceback.format_exc())

            window.hide_loading_snackbar(min_duration_ms=1200, on_finished=show_error)

        thread.finished.connect(on_success)
        thread.failed.connect(on_fail)
        thread.start()

    process_button.clicked.connect(process_file)

    def change_language(language_code):
        global lang
        lang = translations[language_code]
        LanguageManager.set_language(language_code)
        settings.set("language", language_code)
        ui_components.lang = lang
        update_ui()
        window.close_overlay()

    def update_ui():
        try:
            top_bar.title_label.setText(f"{window.window_title_text} {VERSION}")
            minimize_btn.setToolTip(lang["min"])
            close_btn.setToolTip(lang["exit"])
            file_name.set_label(lang["select_file"])
            select_button.setText(lang["sel_button"])
            output_format_text.setText(lang["select_format"])
            radio_raw.setText(".raw")
            radio_png.setText(".png")
            output_size.set_label(lang["select_size"])
            process_button.setText(lang["convert_file"])
            toolbar_buttons["help"].setToolTip(lang["help"])
            toolbar_buttons["language"].setToolTip(lang["cnglang"])
            toolbar_buttons["theme"].setToolTip(lang["toggletheme"])
            social_buttons["github"].setToolTip(lang["github"])
            social_buttons["discord"].setToolTip(lang["discord"])
            social_buttons["telegram"].setToolTip(lang["telegram"])
            social_buttons["youtube"].setToolTip(lang["youtube"])
            toolbar_buttons["mode"].setToolTip(lang["modeswitch2"])
        except Exception as ex:
            logging.error("update_ui error: " + str(ex))

    def show_language_dialog(_e=None):
        lang_dialog = LanguageDialog(window, lang, change_language)
        lang_dialog.show()

    def toggle_theme(_e=None):
        def do_toggle():
            window.theme_mode = "light" if window.theme_mode == "dark" else "dark"
            settings.set("theme", window.theme_mode)
            update_theme()

        window.fade_transition(do_toggle)

    def update_theme():
        colors = ThemeManager.get_theme_colors(window.theme_mode)
        try:
            toolbar_buttons["help"].set_color(colors["icon_color"])
            toolbar_buttons["language"].set_color(colors["icon_color"])
            toolbar_buttons["theme"].set_icon_name(colors["theme_icon"])
            toolbar_buttons["theme"].set_hover_icon_name(colors["theme_icon_hover"])
            toolbar_buttons["theme"].set_color(colors["icon_color"])
            toolbar_buttons["mode"].set_color(colors["icon_color"])
            for key in social_buttons:
                social_buttons[key].set_color(colors["icon_color"])
            pix = QPixmap(colors["logo_src"])
            title_image.setPixmap(pix.scaledToHeight(int(100 * scale_factor), Qt.TransformationMode.SmoothTransformation))
            minimize_btn.set_color(colors["titlebar_btn"])
            close_btn.set_color(colors["titlebar_btn"])
            top_bar.apply_theme(colors)
            output_size.apply_theme(colors)
            file_name.apply_theme(colors)
            select_button.apply_theme(colors)
            process_button.apply_theme(colors)
            window.version_label.setStyleSheet(f"color: {colors['version_color']}; font-size: 10px; background: transparent;")
            output_format_text.setStyleSheet(f"color: {colors['fg']};")

            radio_raw.apply_theme(colors)
            radio_png.apply_theme(colors)

            if hasattr(window, '_update_snackbar') and window._update_snackbar:
                window._update_snackbar.update_theme(colors)
            if hasattr(window, '_loading_snackbar') and window._loading_snackbar:
                window._loading_snackbar.update_theme(colors)

            window.update()
        except Exception as ex:
            logging.debug("update_theme partial: " + str(ex))

    toolbar_buttons = ui_components.create_toolbar_buttons(
        on_help=helpdialog,
        on_language=show_language_dialog,
        on_theme=toggle_theme,
        on_mode_switch=lambda e: switch_to_reverse_ui(window),
        mode_tooltip_key="modeswitch2",
    )
    social_buttons = ui_components.create_social_buttons()
    toolbar_container = ui_components.create_toolbar_container(toolbar_buttons, social_buttons)
    ui_components.create_version_container(on_click=ui_components.show_version_info)

    main_content = QWidget()
    main_content.setStyleSheet("background: transparent;")
    main_layout = QVBoxLayout(main_content)
    main_layout.setContentsMargins(20, 0, 20, 0)
    main_layout.setSpacing(0)
    main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

    spacer = QWidget()
    spacer.setFixedHeight(10)
    main_layout.addWidget(spacer)

    file_col = QVBoxLayout()
    file_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    file_col.addWidget(file_name, alignment=Qt.AlignmentFlag.AlignHCenter)
    gap = QWidget()
    gap.setFixedHeight(10)
    file_col.addWidget(gap)
    file_col.addWidget(select_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    main_layout.addLayout(file_col)

    gap2 = QWidget()
    gap2.setFixedHeight(20)
    main_layout.addWidget(gap2)

    form = QVBoxLayout()
    form.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    form.addWidget(output_format_text)
    gap3 = QWidget()
    gap3.setFixedHeight(10)
    form.addWidget(gap3)
    radios = QHBoxLayout()
    radios.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    radios.addWidget(radio_raw)
    radios.addSpacing(20)
    radios.addWidget(radio_png)
    form.addLayout(radios)
    gap4 = QWidget()
    gap4.setFixedHeight(30)
    form.addWidget(gap4)
    form.addWidget(output_size, alignment=Qt.AlignmentFlag.AlignHCenter)
    gap5 = QWidget()
    gap5.setFixedHeight(30)
    form.addWidget(gap5)
    form.addWidget(process_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    gap6 = QWidget()
    gap6.setFixedHeight(20)
    form.addWidget(gap6)
    main_layout.addLayout(form)
    main_layout.addStretch()

    window.add_ui(main_content, stretch=1)
    window.add_ui(toolbar_container)

    def check_updates():
        thread = UpdateCheckThread(VERSION)
        window._update_check_thread = thread

        def on_info(update_info):
            if not update_info:
                return
            if getattr(update_info, "error", None):
                logging.warning(f"Update check error: {update_info.error}")
                return
            if not getattr(update_info, "update_available", False):
                logging.info(f"No update available. Current: {VERSION}")
                return

            logging.info(f"Update available: {update_info.version}")
            window.show_update_snackbar(update_info, lang)

        thread.result.connect(on_info)
        thread.start()

    global CHECKED_FOR_UPDATES
    if not CHECKED_FOR_UPDATES:
        QTimer.singleShot(200, check_updates)
        CHECKED_FOR_UPDATES = True

    update_theme()
    update_ui()

    if settings.get("first_run", True):
        def show_welcome():
            settings.set("first_run", False)

            colors = ThemeManager.get_theme_colors(window.theme_mode)

            text_label = QLabel(lang["welcome_text"])
            text_label.setTextFormat(Qt.TextFormat.RichText)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(f"color: {colors['text_color']}; font-family: 'Inter'; font-size: 13px; background: transparent;")
            text_label.setFixedWidth(420)

            ui_components.show_themed_dialog(
                "info_outline",
                lang["welcome_title"],
                text_label,
                [(lang["start"], None, colors["button_color"])],
                width=480,
            )

        QTimer.singleShot(600, show_welcome)