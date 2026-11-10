from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QRadioButton,
    QTextEdit, QSlider
)
from localization import translations
from reverse_converter import reverse_converter, struct, RAWNot16BitError, _decode_original_values
from metadata import read_metadata, write_metadata, MetadataError
from packaging.version import parse as parse_pep440, Version as PackVersion, InvalidVersion
import os
import logging
from datetime import datetime
import traceback
import sys
from PIL import Image
from config import VERSION, BUILD, LOG_LEVEL
from ui_components import (
    UIComponents, ThemeManager, LanguageDialog, AppWindow, OutlinedLineEdit, PillButton,
    AnimatedTextButton, _wrap_text, _hex_to_rgb,
    ConversionThread
)
from lang_manager import LanguageManager
from settings_manager import settings

log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

import locale

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error as e:
    logging.warning(f"Failed to set system locale, using default: {e}")

try:
    current_locale = locale.getlocale()[0]
except Exception as e:
    logging.warning(f"Failed to read system locale: {e}")
    current_locale = None

system_lang = current_locale[:2] if current_locale else "En"

_initial_lang_code = system_lang if system_lang in translations else "En"
LanguageManager.set_language(_initial_lang_code)
lang = translations[_initial_lang_code]

FILE_VERSION_FOR_RANGE_EDIT = PackVersion("2.3")


def _parse_version(version_str):
    if not isinstance(version_str, str):
        return None
    stripped = version_str.strip()
    if not stripped:
        return None
    try:
        return parse_pep440(stripped)
    except (InvalidVersion, ValueError):
        return None


def create_back_ui(window: AppWindow, lang_code="En"):
    global lang

    if lang_code is None:
        lang_code = LanguageManager.get_language()

    if lang_code in translations:
        lang = translations[lang_code]
    else:
        lang = translations["En"]

    scale_factor = 1.0

    if any(arg in sys.argv for arg in ("-reverse", "--reverse")):
        window.window_title_text = "DisplaceBox"
        window.setWindowTitle("DisplaceBox")
        window.setFixedSize(580, 680)

    window.clear_ui()

    ui_components = UIComponents(window, lang, scale_factor)

    def switch_to_ui(_page=None):
        from ui import create_ui

        def do_switch():
            logging.info("Switched to \".bin --> .raw/.png\" mode")
            create_ui(window, LanguageManager.get_language())

        window.smooth_transition(do_switch)

    top_bar, minimize_btn, close_btn, topbarico = ui_components.create_top_bar()
    window.add_ui(top_bar)

    title_container, title_image = ui_components.create_title_container()
    window.add_ui(title_container)

    input_file_path = {"value": None}

    def on_file_selected(path):
        nonlocal_path = path
        try:
            if nonlocal_path:
                input_file_path["value"] = nonlocal_path
                file_ext = os.path.splitext(nonlocal_path)[1].lower()

                if file_ext == ".png":
                    try:
                        with Image.open(nonlocal_path) as img:
                            if img.mode != "I" and img.mode != "I;16":
                                ui_components.show_error_dialog(lang["error"], lang["not_16bit_grayscale"])
                                file_name.set_value("")
                                input_file_path["value"] = None
                                logging.error("Selected PNG is not 16-bit grayscale!")
                                return
                            elif img.mode == "I" or img.mode == "I;16":
                                if img.getextrema()[1] > 255:
                                    pass
                                else:
                                    ui_components.show_error_dialog(lang["error"], lang["not_16bit_grayscale"])
                                    file_name.set_value("")
                                    input_file_path["value"] = None
                                    logging.error("Selected PNG is not 16-bit grayscale!")
                                    return
                    except Exception as ex:
                        ui_components.show_error_dialog(lang["error"], lang["invalid_png_file"])
                        file_name.set_value("")
                        input_file_path["value"] = None
                        logging.error(f"Error reading PNG file: {ex}")
                        return
                elif file_ext != ".raw":
                    ui_components.show_error_dialog(lang["error"], lang["wrong_extension_reverse"])
                    file_name.set_value("")
                    input_file_path["value"] = None
                    logging.error("Selected file is not .raw or .png!")
                    return
                elif file_ext == ".raw":
                    try:
                        with open(nonlocal_path, "rb") as f:
                            data_bytes = f.read()
                            if len(data_bytes) % 2 != 0:
                                raise RAWNot16BitError("Input .raw file has incomplete 16-bit data.")
                    except RAWNot16BitError as e:
                        ui_components.show_error_dialog(lang["error"], lang["incomplete_16bit_data"])
                        file_name.set_value("")
                        input_file_path["value"] = None
                        logging.error(f"RAWNot16BitError: {e}")
                        return
                    except Exception as e:
                        ui_components.show_error_dialog(lang["error"], lang["invalid_raw_file"])
                        file_name.set_value("")
                        input_file_path["value"] = None
                        logging.error(f"Error reading RAW file: {e}")
                        return
            else:
                logging.info("User closed file picker without selecting a file.")
                return
        except AttributeError:
            logging.info("User closed file picker.")
            return

        file_name.set_value(input_file_path["value"])

    json_file_path = {"value": None}
    json_data = {"value": {}}
    original_range = {"value": None}
    current_range = {"value": None}
    ssl_maxheight = {"value": None}
    range_edit_allowed = {"value": True}

    def has_original_values():
        return isinstance(json_data["value"], dict) and "OriginalValues" in json_data["value"]

    def get_ssl_maxheight(json_path):
        try:
            json_dir = os.path.dirname(json_path)
            map_name = os.path.basename(json_dir)
            parent_dir = os.path.dirname(json_dir)
            ssl_path = os.path.join(parent_dir, f"{map_name}.ssl")

            if not os.path.exists(ssl_path):
                return None

            import xml.etree.ElementTree as ET
            tree = ET.parse(ssl_path)
            root = tree.getroot()

            for key in root.findall(".//Key"):
                if key.get("name") == "MAXHEIGHT":
                    return float(key.text.strip())
            return None
        except Exception as e:
            logging.warning(f"Failed to read MAXHEIGHT from SSL: {e}")
            return None

    def update_range_label():
        colors = ThemeManager.get_theme_colors(window.theme_mode)
        if current_range["value"]:
            mn = current_range["value"]["min"]
            mx = current_range["value"]["max"]
            orig = original_range["value"]
            is_custom = False
            if orig:
                is_custom = abs(mn - orig["min"]) > 0.01 or abs(mx - orig["max"]) > 0.01
            color = "#E65100" if is_custom else colors["muted"]
            range_label.setText(f"{lang['range_editor_current']}: {mn:.1f} – {mx:.1f}")
            range_label.setStyleSheet(f"color: {color}; font-size: 12px; font-family: 'Inter'; background: transparent;")
            edit_range_btn.setVisible(range_edit_allowed["value"])
        else:
            range_label.setText("")
            edit_range_btn.setVisible(False)

    def show_range_dialog(_e=None):
        if not current_range["value"]:
            return
        if not range_edit_allowed["value"]:
            logging.info("Range editing blocked for this metadata version")
            return

        dlg_colors = ThemeManager.get_theme_colors(window.theme_mode)

        orig_min = original_range["value"]["min"]
        orig_max = original_range["value"]["max"]
        cur_min = current_range["value"]["min"]
        cur_max = current_range["value"]["max"]

        ssl_limit = ssl_maxheight["value"] if ssl_maxheight["value"] else None

        slider_low = int(min(0, orig_min - 100, cur_min - 100))
        slider_high = int(max(ssl_limit or 2500, orig_max + 100, cur_max + 100))
        if slider_high <= slider_low:
            slider_high = slider_low + 100

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        orig_info = QLabel(f"{lang['range_editor_original']}: {orig_min:.1f} – {orig_max:.1f}")
        orig_info.setStyleSheet(f"color: {dlg_colors['muted']}; font-size: 12px; font-family: 'Inter'; background: transparent;")
        layout.addWidget(orig_info)

        if ssl_limit:
            ssl_hint = QLabel(f"{lang['range_editor_ssl_hint']}: {ssl_limit:.1f}")
            ssl_hint.setStyleSheet(f"color: {dlg_colors['muted']}; font-size: 12px; font-family: 'Inter'; background: transparent;")
            layout.addWidget(ssl_hint)

        if not has_original_values():
            warn_lbl = QLabel(lang.get(
                "range_editor_no_original",
                " This JSON has no original values. Expanding the range will affect the entire map."
            ))
            warn_lbl.setWordWrap(True)
            warn_lbl.setStyleSheet(f"color: #E65100; font-size: 12px; font-family: 'Inter'; background: transparent;")
            layout.addWidget(warn_lbl)

        bc_r, bc_g, bc_b = _hex_to_rgb(dlg_colors['border_color'])
        slider_qss = f"""
            QSlider::groove:horizontal {{
                border: none;
                background: rgba({bc_r}, {bc_g}, {bc_b}, 0.5);
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {dlg_colors['icon_color']};
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {dlg_colors['icon_color']};
                border-radius: 3px;
            }}
        """

        min_label = QLabel(lang["range_editor_min"])
        min_label.setStyleSheet(f"color: {dlg_colors['text_color']}; font-size: 12px; font-family: 'Inter'; font-weight: 600; background: transparent;")
        layout.addWidget(min_label)

        min_row = QWidget()
        min_row_l = QHBoxLayout(min_row)
        min_row_l.setContentsMargins(0, 0, 0, 0)
        min_row_l.setSpacing(10)

        min_slider = QSlider(Qt.Orientation.Horizontal)
        min_slider.setRange(slider_low, slider_high)
        min_slider.setValue(int(round(cur_min)))
        min_slider.setStyleSheet(slider_qss)

        min_input = OutlinedLineEdit("", width=130, read_only=False)
        min_input.apply_theme(dlg_colors)
        min_input.set_value(f"{cur_min:.2f}")

        min_row_l.addWidget(min_slider, stretch=1)
        min_row_l.addWidget(min_input)
        layout.addWidget(min_row)

        max_label = QLabel(lang["range_editor_max"])
        max_label.setStyleSheet(f"color: {dlg_colors['text_color']}; font-size: 12px; font-family: 'Inter'; font-weight: 600; background: transparent;")
        layout.addWidget(max_label)

        max_row = QWidget()
        max_row_l = QHBoxLayout(max_row)
        max_row_l.setContentsMargins(0, 0, 0, 0)
        max_row_l.setSpacing(10)

        max_slider = QSlider(Qt.Orientation.Horizontal)
        max_slider.setRange(slider_low, slider_high)
        max_slider.setValue(int(round(cur_max)))
        max_slider.setStyleSheet(slider_qss)

        max_input = OutlinedLineEdit("", width=130, read_only=False)
        max_input.apply_theme(dlg_colors)
        max_input.set_value(f"{cur_max:.2f}")

        max_row_l.addWidget(max_slider, stretch=1)
        max_row_l.addWidget(max_input)
        layout.addWidget(max_row)

        delta_lbl = QLabel("")
        delta_lbl.setStyleSheet(f"color: {dlg_colors['muted']}; font-size: 12px; font-family: 'Inter'; background: transparent;")
        delta_lbl.setWordWrap(True)
        layout.addWidget(delta_lbl)

        def _update_delta():
            try:
                mn = float(min_input.value())
                mx = float(max_input.value())
                if mx < mn:
                    delta_lbl.setText(f"{lang['range_editor_invalid']}")
                    delta_lbl.setStyleSheet(f"color: #FF5252; font-size: 12px; font-family: 'Inter'; background: transparent;")
                elif ssl_limit and mx > ssl_limit:
                    delta_lbl.setText(f"{lang['range_editor_over_limit']} (Delta: {mx - mn:.1f})")
                    delta_lbl.setStyleSheet(f"color: #E65100; font-size: 12px; font-family: 'Inter'; background: transparent;")
                else:
                    delta_lbl.setText(f"Delta: {mx - mn:.1f}")
                    delta_lbl.setStyleSheet(f"color: {dlg_colors['muted']}; font-size: 12px; font-family: 'Inter'; background: transparent;")
            except ValueError:
                delta_lbl.setText(f"{lang['range_editor_invalid']}")
                delta_lbl.setStyleSheet(f"color: #FF5252; font-size: 12px; font-family: 'Inter'; background: transparent;")

        def _on_min_slider(v):
            min_input.set_value(f"{float(v):.2f}")

        def _on_min_input(_text):
            try:
                val = float(min_input.value())
                val_clamped = max(slider_low, min(slider_high, val))
                if min_slider.value() != int(round(val_clamped)):
                    min_slider.blockSignals(True)
                    min_slider.setValue(int(round(val_clamped)))
                    min_slider.blockSignals(False)
                _update_delta()
            except ValueError:
                pass

        def _on_max_slider(v):
            max_input.set_value(f"{float(v):.2f}")

        def _on_max_input(_text):
            try:
                val = float(max_input.value())
                val_clamped = max(slider_low, min(slider_high, val))
                if max_slider.value() != int(round(val_clamped)):
                    max_slider.blockSignals(True)
                    max_slider.setValue(int(round(val_clamped)))
                    max_slider.blockSignals(False)
                _update_delta()
            except ValueError:
                pass

        min_slider.valueChanged.connect(_on_min_slider)
        min_input.edit.textChanged.connect(_on_min_input)
        max_slider.valueChanged.connect(_on_max_slider)
        max_input.edit.textChanged.connect(_on_max_input)

        _update_delta()

        def _apply():
            try:
                mn = float(min_input.value())
                mx = float(max_input.value())
                if mx < mn:
                    ui_components.show_error_dialog(lang["error"], lang["range_editor_invalid"])
                    return
                current_range["value"] = {"min": mn, "max": mx}
                logging.info(
                    f"Range APPLIED: {mn:.2f} – {mx:.2f} "
                    f"(original was {orig_min:.2f} – {orig_max:.2f})"
                )
                update_range_label()
                window.close_overlay()
            except ValueError:
                ui_components.show_error_dialog(lang["error"], lang["range_editor_invalid"])

        def _reset():
            min_slider.setValue(int(round(orig_min)))
            max_slider.setValue(int(round(orig_max)))
            min_input.set_value(f"{orig_min:.2f}")
            max_input.set_value(f"{orig_max:.2f}")
            _update_delta()

        ui_components.show_themed_dialog(
            "info_outline",
            lang["range_editor_title"],
            content,
            [
                (lang["range_editor_reset"], _reset, dlg_colors["button_color"]),
                (lang["range_editor_apply"], _apply, dlg_colors["button_color"]),
            ],
            width=540,
        )

    def on_json_selected(path):
        if not path:
            logging.info("JSON file selection canceled.")
            return

        json_file_path["value"] = path
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext not in (".dgc", ".json"):
            ui_components.show_error_dialog(lang["error"], lang["wrong_extension_json"])
            json_file_path["value"] = None
            json_field.set_value("")
            json_data["value"] = {}
            original_range["value"] = None
            current_range["value"] = None
            ssl_maxheight["value"] = None
            range_edit_allowed["value"] = True
            update_range_label()
            return

        is_legacy_json = ext == ".json"

        def _close_all_overlays():
            while window._extra_overlays:
                window.close_overlay()
            window.close_overlay()

        def _reset_state():
            json_file_path["value"] = None
            json_data["value"] = {}
            json_field.set_value("")
            original_range["value"] = None
            current_range["value"] = None
            ssl_maxheight["value"] = None
            range_edit_allowed["value"] = True
            update_range_label()
            _close_all_overlays()

        def _load_and_validate():
            try:
                json_data["value"] = read_metadata(path)
            except MetadataError as ex:
                logging.error(f"Metadata read error: {ex}")
                ui_components.show_error_dialog(lang["error"], lang["invalid_json_metadata"])
                _reset_state()
                return
            except Exception as ex:
                logging.error(f"Ошибка чтения JSON: {ex}")
                ui_components.show_error_dialog(lang["error"], lang["invalid_json_metadata"])
                _reset_state()
                return

            _validate()

        def _validate():
            required_keys = ["Min", "Max", "Delta"]
            missing_keys = [key for key in required_keys if key not in json_data["value"]]
            if missing_keys:
                error_msg = lang.get(
                    "invalid_json_missing_keys",
                    "Missing required keys: {keys}"
                ).format(keys=", ".join(missing_keys))
                ui_components.show_error_dialog(lang["error"], error_msg)
                _reset_state()
                return

            dgcver = json_data["value"].get("DGCVer")

            if not dgcver or not dgcver.startswith("DisplaceGUI_"):
                ui_components.show_error_dialog(lang["error"], lang["invalid_json_dgcver"])
                _reset_state()
                return

            file_version_str = dgcver[len("DisplaceGUI_"):]

            file_ver = _parse_version(file_version_str)
            current_ver = _parse_version(VERSION)

            if file_ver is None or current_ver is None:
                logging.error(
                    f"Version parse failed: file='{file_version_str}', current='{VERSION}'"
                )
                ui_components.show_error_dialog(lang["error"], lang["invalid_json_version_format"])
                _reset_state()
                return

            def proceed_with_selection():
                range_edit_allowed["value"] = file_ver >= FILE_VERSION_FOR_RANGE_EDIT
                json_field.set_value(json_file_path["value"])
                json_field.edit.deselect()

                cur_min_val = float(json_data["value"]["Min"])
                cur_max_val = float(json_data["value"]["Max"])

                if "OriginalMin" in json_data["value"] and "OriginalMax" in json_data["value"]:
                    orig_min_val = float(json_data["value"]["OriginalMin"])
                    orig_max_val = float(json_data["value"]["OriginalMax"])
                else:
                    orig_min_val = cur_min_val
                    orig_max_val = cur_max_val

                original_range["value"] = {"min": orig_min_val, "max": orig_max_val}
                current_range["value"] = {"min": cur_min_val, "max": cur_max_val}
                ssl_maxheight["value"] = get_ssl_maxheight(json_file_path["value"])
                logging.info(
                    f"Metadata accepted: version {file_ver}, current {current_ver}, "
                    f"original={orig_min_val:.2f}–{orig_max_val:.2f}, "
                    f"current={cur_min_val:.2f}–{cur_max_val:.2f}, "
                    f"range_edit_allowed={range_edit_allowed['value']}"
                )
                update_range_label()
                _close_all_overlays()

            if file_ver < FILE_VERSION_FOR_RANGE_EDIT:
                msg = lang.get(
                    "json_from_older_version_edit_disabled",
                    "The metadata was created in an older version ({file_version}).\n"
                    "Height editing requires version {min_version} or newer.\n"
                    "The height range editor will be disabled.\n\nContinue?"
                ).format(
                    file_version=str(file_ver),
                    min_version=str(FILE_VERSION_FOR_RANGE_EDIT),
                )
                ui_components.show_colored_dialog(
                    "#E65100",
                    "warning",
                    lang["warning"],
                    msg,
                    [(lang["yes"], proceed_with_selection), (lang["no"], _reset_state)],
                )
                return

            if file_ver > current_ver:
                ui_components.show_colored_dialog(
                    "#E65100",
                    "warning",
                    lang["warning"],
                    lang["json_from_newer_version"],
                    [(lang["yes"], proceed_with_selection), (lang["no"], _reset_state)],
                )
                return

            if file_ver < current_ver:
                ui_components.show_colored_dialog(
                    "#E65100",
                    "warning",
                    lang["warning"],
                    lang["json_from_older_version"],
                    [(lang["yes"], proceed_with_selection), (lang["no"], _reset_state)],
                )
                return

            proceed_with_selection()

        if is_legacy_json:
            ui_components.show_colored_dialog(
                "#E65100",
                "warning",
                lang["warning"],
                lang.get(
                    "legacy_json_warning",
                    "The selected file uses the legacy JSON metadata format.\n"
                    "This format is deprecated and may produce incorrect results.\n\n"
                    "Continue anyway?"
                ),
                [(lang["yes"], _load_and_validate), (lang["no"], _reset_state)],
            )
            return

        _load_and_validate()

    def select_file(_e=None):
        last_dir = settings.get("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(window, lang["sel_button"], last_dir, "RAW/PNG (*.raw *.png);;All files (*.*)")
        if path:
            settings.set("last_dir", os.path.dirname(path))
        on_file_selected(path)

    def select_json(_e=None):
        last_dir = settings.get("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(
            window, lang["sel_button"], last_dir,
            "Metadata (*.dgc *.json);;DGC (*.dgc);;Legacy JSON (*.json);;All files (*.*)"
        )
        if path:
            settings.set("last_dir", os.path.dirname(path))
        on_json_selected(path)

    def helpdialog(_e=None):
        colors = ThemeManager.get_theme_colors(window.theme_mode)

        notes = QTextEdit()
        notes.setReadOnly(True)
        notes.setPlainText(lang["reversehelp_text"])
        notes.setFixedSize(450, 400)

        scrollbar_qss = f"""
            QTextEdit {{
                background: transparent;
                color: {colors['text_color']};
                border: none;
                font-family: 'Inter';
                font-size: 13px;
                padding-right: 15px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['muted']};
                min-height: 30px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['icon_color']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                height: 0px;
            }}
        """
        notes.setStyleSheet(scrollbar_qss)

        ui_components.show_themed_dialog("info_outline", lang["help"], notes, [("OK", None, None)], width=500)

    def process_file(_e=None):
        data = json_data["value"]
        if not data or "Min" not in data or "Max" not in data or "Delta" not in data:
            ui_components.show_colored_dialog(
                "#B71C1C",
                "warning",
                lang["error"],
                lang["invalid_json_metadata"],
                [("OK", None)],
            )
            return

        if not input_file_path["value"]:
            ui_components.show_colored_dialog(
                "#B71C1C",
                "warning",
                lang["error"],
                lang["plssel_file"],
                [("OK", None)],
            )
            logging.warning("File is not selected!")
            return

        _, input_ext = os.path.splitext(input_file_path["value"])
        input_ext = input_ext.lower()
        if input_ext not in [".raw", ".png"]:
            ui_components.show_colored_dialog(
                "#B71C1C",
                "warning",
                lang["error"],
                lang["wrong_extension_reverse"],
                [("OK", None)],
            )
            return

        custom_range = None
        if current_range["value"] and original_range["value"]:
            curr = current_range["value"]
            orig = original_range["value"]
            if abs(curr["min"] - orig["min"]) > 0.01 or abs(curr["max"] - orig["max"]) > 0.01:
                custom_range = (curr["min"], curr["max"])
                logging.info(f"Custom range DETECTED: {custom_range} (will trigger smart restore)")
            else:
                logging.info(f"No range change: {curr['min']:.2f} – {curr['max']:.2f} matches original, using default conversion")
        else:
            logging.info("No custom range set (current_range or original_range is empty)")

        output_path = os.path.splitext(input_file_path["value"])[0] + ".bin"

        process_button.setEnabled(False)
        window.show_loading_snackbar(lang.get("converting", "Converting..."))

        thread = ConversionThread(
            reverse_converter,
            input_file_path["value"],
            output_path,
            data,
            custom_range,
        )
        window._conversion_thread = thread

        def on_success(result):
            _min, _max, _del = result

            extra = [
                _wrap_text(f"{lang['file_saved']}:", "#FFFFFF", 14, bold=True),
                _wrap_text(output_path, "#FFFFFF", 12),
                _wrap_text(f"{lang['range_editor_current']}: {_min:.1f} – {_max:.1f}", "#FFFFFF", 11),
            ]

            def show_result():
                process_button.setEnabled(True)
                ui_components.show_colored_dialog(
                    "#0A8A3C",
                    "check",
                    lang["result"],
                    None,
                    [("OK", None)],
                    extra_widgets=extra,
                    on_dismiss=lambda: logging.info(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}"),
                )
                logging.info(f"Converted file saved to: {output_path}")

                if custom_range:
                    try:
                        if 'OriginalMin' not in data or 'OriginalMax' not in data or 'OriginalDelta' not in data:
                            orig_floats = _decode_original_values(data, expected_length=None)
                            if orig_floats:
                                data['OriginalMin'] = float(min(orig_floats))
                                data['OriginalMax'] = float(max(orig_floats))
                                data['OriginalDelta'] = float(max(orig_floats) - min(orig_floats))
                                logging.info(
                                    f"Backfilled OriginalMin/Max/Delta from OriginalValues: "
                                    f"{data['OriginalMin']:.2f} – {data['OriginalMax']:.2f}"
                                )
                            else:
                                data['OriginalMin'] = float(data['Min'])
                                data['OriginalMax'] = float(data['Max'])
                                data['OriginalDelta'] = float(data['Delta'])
                                logging.info(
                                    f"Backfilled OriginalMin/Max/Delta from current Min/Max/Delta "
                                    f"(no OriginalValues available): "
                                    f"{data['OriginalMin']:.2f} – {data['OriginalMax']:.2f}"
                                )

                        data['Min'] = float(custom_range[0])
                        data['Max'] = float(custom_range[1])
                        data['Delta'] = float(custom_range[1]) - float(custom_range[0])

                        old_path = json_file_path["value"]
                        new_path = os.path.splitext(old_path)[0] + ".dgc"
                        write_metadata(new_path, data)

                        if new_path != old_path:
                            try:
                                os.remove(old_path)
                                logging.info(f"Migrated legacy metadata: {old_path} -> {new_path}")
                            except Exception as e:
                                logging.warning(f"Failed to remove legacy metadata {old_path}: {e}")
                            json_file_path["value"] = new_path
                            json_field.set_value(new_path)

                        json_data["value"] = data
                        if 'OriginalMin' in data and 'OriginalMax' in data:
                            original_range["value"] = {"min": data['OriginalMin'], "max": data['OriginalMax']}
                        else:
                            original_range["value"] = {"min": data['Min'], "max": data['Max']}
                        update_range_label()
                        logging.info(
                            f"Metadata saved: {new_path}, "
                            f"new range {custom_range}, "
                            f"original preserved as "
                            f"({data['OriginalMin']:.2f} – {data['OriginalMax']:.2f})"
                        )
                    except Exception as e:
                        logging.error(f"Failed to update metadata: {e}")

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
                        [("OK", None), (lang["help"], lambda: helpdialog())],
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
                elif isinstance(e, ValueError):
                    ui_components.show_colored_dialog(
                        "#D50000",
                        "error",
                        lang["error"],
                        lang["unsupportedfile"],
                        [
                            ("OK", None),
                            (lang["opengit"], lambda: window.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new")),
                        ],
                    )
                    logging.error(f"ValueError occurred: {e}")
                else:
                    ui_components.show_error_dialog(lang["error"], str(e))
                    logging.error(f"Unexpected error: {e}")

                logging.error("Traceback:\n" + traceback.format_exc())

            window.hide_loading_snackbar(min_duration_ms=1200, on_finished=show_error)

        thread.finished.connect(on_success)
        thread.failed.connect(on_fail)
        thread.start()

    def change_language(language_code):
        global lang
        lang = translations[language_code]
        LanguageManager.set_language(language_code)
        settings.set("language", language_code)
        ui_components.lang = lang
        update_ui()
        window.close_overlay()

    def update_ui():
        top_bar.title_label.setText(f"{window.window_title_text} {VERSION}")
        minimize_btn.setToolTip(lang["min"])
        close_btn.setToolTip(lang["exit"])
        file_name.set_label(lang["select_file"])
        select_button.setText(lang["sel_button"])
        process_button.setText(lang["convert_file"])
        toolbar_buttons["help"].setToolTip(lang["help"])
        toolbar_buttons["language"].setToolTip(lang["cnglang"])
        toolbar_buttons["theme"].setToolTip(lang["toggletheme"])
        social_buttons["github"].setToolTip(lang["github"])
        social_buttons["discord"].setToolTip(lang["discord"])
        social_buttons["telegram"].setToolTip(lang["telegram"])
        social_buttons["youtube"].setToolTip(lang["youtube"])
        toolbar_buttons["mode"].setToolTip(lang["modeswitch1"])
        json_field.set_label(lang["json"])
        select_json_button.setText(lang["sel_button"])
        edit_range_btn.setText(lang["range_editor_edit"])
        update_range_label()

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
        json_field.apply_theme(colors)
        file_name.apply_theme(colors)
        select_button.apply_theme(colors)
        process_button.apply_theme(colors)
        select_json_button.apply_theme(colors)
        window.version_label.setStyleSheet(f"color: {colors['version_color']}; font-size: 10px; background: transparent;")

        if hasattr(window, '_update_snackbar') and window._update_snackbar:
            window._update_snackbar.update_theme(colors)
        if hasattr(window, '_loading_snackbar') and window._loading_snackbar:
            window._loading_snackbar.update_theme(colors)

        update_range_label()
        window.update()

    file_name = OutlinedLineEdit(lang["select_file"], width=int(400 * scale_factor))
    select_button = PillButton(lang["sel_button"], hpad=int(20 * scale_factor), vpad=int(10 * scale_factor), font_size=int(14 * scale_factor))
    select_button.clicked.connect(select_file)

    json_field = OutlinedLineEdit(lang["json"], width=int(400 * scale_factor))
    select_json_button = PillButton(lang["sel_button"], hpad=int(20 * scale_factor), vpad=int(10 * scale_factor), font_size=int(14 * scale_factor))
    select_json_button.clicked.connect(select_json)

    colors_main = ThemeManager.get_theme_colors(window.theme_mode)
    range_row = QWidget()
    range_layout = QHBoxLayout(range_row)
    range_layout.setContentsMargins(0, 0, 0, 0)
    range_layout.setSpacing(8)
    range_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    range_label = QLabel("")
    range_label.setStyleSheet(f"color: {colors_main['muted']}; font-size: 12px; font-family: 'Inter'; background: transparent;")
    range_layout.addWidget(range_label)

    edit_range_btn = AnimatedTextButton(lang["range_editor_edit"], colors_main["button_color"])
    edit_range_btn.setVisible(False)
    edit_range_btn.clicked.connect(show_range_dialog)
    range_layout.addWidget(edit_range_btn)

    process_button = PillButton(lang["convert_file"], hpad=int(30 * scale_factor), vpad=int(10 * scale_factor), font_size=int(14 * scale_factor))
    process_button.clicked.connect(process_file)

    toolbar_buttons = ui_components.create_toolbar_buttons(
        on_help=helpdialog,
        on_language=show_language_dialog,
        on_theme=toggle_theme,
        on_mode_switch=lambda e: switch_to_ui(window),
        mode_tooltip_key="modeswitch1",
    )
    social_buttons = ui_components.create_social_buttons()
    toolbar_container = ui_components.create_toolbar_container(toolbar_buttons, social_buttons)
    ui_components.create_version_container(on_click=ui_components.show_version_info)

    body = QWidget()
    body.setStyleSheet("background: transparent;")
    body_l = QVBoxLayout(body)
    body_l.setContentsMargins(20, 0, 20, 0)
    body_l.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

    file_col = QVBoxLayout()
    file_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    file_col.addWidget(file_name, alignment=Qt.AlignmentFlag.AlignHCenter)
    file_col.addWidget(select_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    body_l.addLayout(file_col)
    gap = QWidget()
    gap.setFixedHeight(20)
    body_l.addWidget(gap)

    json_col = QVBoxLayout()
    json_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    json_col.addWidget(json_field, alignment=Qt.AlignmentFlag.AlignHCenter)
    json_col.addWidget(select_json_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    json_col.addWidget(range_row, alignment=Qt.AlignmentFlag.AlignHCenter)
    body_l.addLayout(json_col)
    gap2 = QWidget()
    gap2.setFixedHeight(20)
    body_l.addWidget(gap2)

    body_l.addWidget(process_button, alignment=Qt.AlignmentFlag.AlignHCenter)
    gap3 = QWidget()
    gap3.setFixedHeight(30)
    body_l.addWidget(gap3)
    body_l.addStretch()

    window.add_ui(body, stretch=1)
    window.add_ui(toolbar_container)

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