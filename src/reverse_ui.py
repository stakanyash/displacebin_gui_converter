import flet as ft
import locale
from localization import translations
from reverse_converter import reverse_converter, struct, RAWNot16BitError
import os
from resources import get_asset_path
import logging
from datetime import datetime
import traceback
import sys
from PIL import Image
from config import VERSION, BUILD
from ui_components import UIComponents, ThemeManager, LanguageDialog
from lang_manager import LanguageManager

log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

locale.setlocale(locale.LC_ALL, '')
current_locale = locale.getlocale()[0]
system_lang = current_locale[:2] if current_locale else 'En'

lang = LanguageManager.set_language(system_lang if system_lang in translations else 'En')

class PageHelper:
    def __init__(self, page: ft.Page):
        self.page = page

    def minimize(self, e):
        self.page.window.minimized = True
        self.page.update()

    def close(self, e):
        self.page.window.close()

def create_back_ui(page: ft.Page, lang_code="En"):
    global lang
    
    if lang_code is None:
        lang_code = LanguageManager.get_language()
    
    if lang_code in translations:
        lang = translations[lang_code]
    else:
        lang = translations["En"]

    scale_factor = 1.0

    if any(arg in sys.argv for arg in ("-reverse", "--reverse")):
        page.title = "DisplaceBox"
        page.window.maximizable = False
        page.window.width = 580 
        page.window.height = 680
        page.window.resizable = False
        page.window.title_bar_hidden = True
        page.window.title_bar_buttons_hidden = True
        page.window.icon = get_asset_path('icon.ico')
        page.window.center()

    helper = PageHelper(page)
    ui_components = UIComponents(page, lang, scale_factor)

    def switch_to_ui(page: ft.Page):
        from ui import create_ui
        page.clean()
        logging.info("Switched to \".bin --> .raw/.png\" mode")
        create_ui(page, LanguageManager.get_language())

    top_bar, minimize_btn, close_btn, topbarico = ui_components.create_top_bar(helper)
    page.add(top_bar)

    title_container, title_image = ui_components.create_title_container()

    page.add(
        ft.Column(
            [title_container],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=False
        )
    )

    input_file_path = None

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal input_file_path
        try:
            if e.files:
                input_file_path = e.files[0].path
                file_ext = os.path.splitext(input_file_path)[1].lower()

                if file_ext == ".png":
                    try:
                        with Image.open(input_file_path) as img:
                            if img.mode != 'I' and img.mode != 'I;16':
                                ui_components.show_error_dialog(lang["error"], lang["not_16bit_grayscale"])
                                file_name.value = ""
                                input_file_path = None
                                logging.error("Selected PNG is not 16-bit grayscale!")
                                page.update()
                                return
                            elif img.mode == 'I' or img.mode == 'I;16':
                                if img.getextrema()[1] > 255:
                                    pass
                                else:
                                    ui_components.show_error_dialog(lang["error"], lang["not_16bit_grayscale"])
                                    file_name.value = ""
                                    input_file_path = None
                                    logging.error("Selected PNG is not 16-bit grayscale!")
                                    page.update()
                                    return

                    except Exception as ex:
                        ui_components.show_error_dialog(lang["error"], lang["invalid_png_file"])
                        file_name.value = ""
                        input_file_path = None
                        logging.error(f"Error reading PNG file: {ex}")
                        page.update()
                        return
                elif file_ext != ".raw":
                    ui_components.show_error_dialog(lang["error"], lang["wrong_extension_reverse"])
                    file_name.value = ""
                    input_file_path = None
                    logging.error("Selected file is not .raw or .png!")
                    page.update()
                    return
                elif file_ext == ".raw":
                    try:
                        with open(input_file_path, "rb") as f:
                            data_bytes = f.read()
                            if len(data_bytes) % 2 != 0:
                                raise RAWNot16BitError("Input .raw file has incomplete 16-bit data.")
                    except RAWNot16BitError as e:
                        ui_components.show_error_dialog(lang["error"], lang["incomplete_16bit_data"])
                        file_name.value = ""
                        input_file_path = None
                        logging.error(f"RAWNot16BitError: {e}")
                        page.update()
                        return
                    except Exception as e:
                        ui_components.show_error_dialog(lang["error"], lang["invalid_raw_file"])
                        file_name.value = ""
                        input_file_path = None
                        logging.error(f"Error reading RAW file: {e}")
                        page.update()
                        return

            else:
                logging.info("User closed file picker without selecting a file.")
                return

        except AttributeError:
            logging.info("User closed file picker.")
            return

        file_name.value = input_file_path
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    json_file_path = None
    json_data = {}

    def on_json_selected(e: ft.FilePickerResultEvent):
        nonlocal json_file_path, json_data
        if e.files:
            json_file_path = e.files[0].path
            _, ext = os.path.splitext(json_file_path)
            if ext.lower() != ".json":
                ui_components.show_error_dialog(lang["error"], lang["wrong_extension_json"])
                json_file_path = None
                json_field.value = ""
                json_data = {}
                page.update()
                return

            try:
                import json
                with open(json_file_path, "r") as f:
                    json_data = json.load(f)

                required_keys = ["Min", "Max", "Delta"]
                missing_keys = [key for key in required_keys if key not in json_data]
                if missing_keys:
                    error_msg = lang["invalid_json_missing_keys"].format(keys=", ".join(missing_keys))
                    ui_components.show_error_dialog(lang["error"], error_msg)
                    json_file_path = None
                    json_data = {}
                    json_field.value = ""
                    page.update()
                    return

                dgcver = json_data.get("DGCVer")
                current_version = VERSION

                if not dgcver or not dgcver.startswith("DisplaceGUI_"):
                    ui_components.show_error_dialog(lang["error"], lang["invalid_json_dgcver"])
                    json_file_path = None
                    json_data = {}
                    json_field.value = ""
                    page.update()
                    return

                file_version_str = dgcver[len("DisplaceGUI_"):]

                def parse_version(version_str):
                    parts = version_str.split(".")
                    try:
                        major = int(parts[0])
                        minor = int(parts[1]) if len(parts) > 1 else 0
                    except (IndexError, ValueError):
                        return None, None
                    return major, minor

                file_major, file_minor = parse_version(file_version_str)
                current_major, current_minor = parse_version(current_version)

                if file_major is None or current_major is None:
                    ui_components.show_error_dialog(lang["error"], lang["invalid_json_version_format"])
                    json_file_path = None
                    json_data = {}
                    json_field.value = ""
                    page.update()
                    return

                def proceed_with_selection():
                    json_field.value = json_file_path
                    page.update()

                def cancel_selection():
                    nonlocal json_file_path, json_data
                    json_file_path = None
                    json_data = {}
                    json_field.value = ""
                    page.update()

                if file_major < current_major or (file_major == current_major and file_minor < current_minor):
                    def show_confirm_dialog():
                        def close_dialog():
                            dlg.open = False
                            page.update()

                        dlg = ft.AlertDialog(
                            open=True,
                            bgcolor=ft.Colors.ORANGE_900,
                            title=ft.Row(
                                [
                                    ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                                    ft.Text(lang["warning"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                                ],
                            ),
                            content=ft.Text(lang["json_from_older_version"], color=ft.Colors.WHITE),
                            actions=[
                                ft.TextButton(lang["yes"], on_click=lambda _: [close_dialog(), proceed_with_selection()], style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                                ft.TextButton(lang["no"], on_click=lambda _: [close_dialog(), cancel_selection()], style=ft.ButtonStyle(color=ft.Colors.WHITE))
                            ],
                            actions_alignment=ft.MainAxisAlignment.END
                        )
                        
                        page.overlay.append(dlg)
                        page.update()

                    show_confirm_dialog()
                    return

                elif file_major > current_major or (file_major == current_major and file_minor > current_minor):
                    def show_confirm_dialog():
                        def close_dialog():
                            dlg.open = False
                            page.update()
                        
                        dlg = ft.AlertDialog(
                            open=True,
                            bgcolor=ft.Colors.ORANGE_900,
                            title=ft.Row(
                                [
                                    ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                                    ft.Text(lang["warning"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                                ],
                            ),
                            content=ft.Text(lang["json_from_newer_version"], color=ft.Colors.WHITE),
                            actions=[
                                ft.TextButton(lang["yes"], on_click=lambda _: [close_dialog(), proceed_with_selection()], style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                                ft.TextButton(lang["no"], on_click=lambda _: [close_dialog(), cancel_selection()], style=ft.ButtonStyle(color=ft.Colors.WHITE))
                            ],
                            actions_alignment=ft.MainAxisAlignment.END
                        )
                        page.overlay.append(dlg)
                        page.update()

                    show_confirm_dialog()
                    return

                else:
                    json_field.value = json_file_path
                    page.update()

            except Exception as ex:
                logging.error(f"Ошибка чтения JSON: {ex}")
                ui_components.show_error_dialog(lang["error"], lang["invalid_json_metadata"])
                json_file_path = None
                json_data = {}
                json_field.value = ""
            page.update()
        else:
            logging.info("JSON file selection canceled.")
            page.update()

    json_picker = ft.FilePicker(on_result=on_json_selected)
    page.overlay.append(json_picker)

    def select_file(e):
        file_picker.pick_files()

    icon_help_title = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=ft.Colors.WHITE)
    text_help_title = ft.Text(lang["help"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)

    def helpdialog(e):
        def close_dlghelp(e):
            help_dlg.open = False
            page.update()

        help_dlg = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    icon_help_title,
                    text_help_title,
                ],
            ),
            content=ft.Container(
                content=ft.ListView(
                    [ft.Text(
                        lang["reversehelp_text"],
                        selectable=True,
                        no_wrap=False,
                        expand=True
                    )],
                    spacing=10,
                    height=300,
                    expand=True
                ),
                width=450,
                height=400,
                padding=10,
            ),
            actions=[
                ft.TextButton("OK", on_click=close_dlghelp)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(help_dlg)
        page.update()

    def process_file(e):
        if not json_data or "Min" not in json_data or "Max" not in json_data or "Delta" not in json_data:
            def close_invalid_json(e):
                invalid_json_dlg.open = False
                page.update()
            invalid_json_dlg = ft.AlertDialog(
                open=True,
                bgcolor=ft.Colors.RED_900,
                title=ft.Row(
                    [ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE), ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                ),
                content=ft.Text(lang["invalid_json_metadata"], color=ft.Colors.WHITE),
                actions=[
                    ft.TextButton("OK", on_click=close_invalid_json, style=ft.ButtonStyle(color=ft.Colors.WHITE))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(invalid_json_dlg)
            page.update()
            return

        if input_file_path:
            _, input_ext = os.path.splitext(input_file_path)
            input_ext = input_ext.lower()
            if input_ext not in [".raw", ".png"]:
                def close_invalid_input(e):
                    invalid_input_dialog.open = False
                    page.update()
                invalid_input_dialog = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["wrong_extension_reverse"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=close_invalid_input, style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(invalid_input_dialog)
                page.update()
                return

            output_path = os.path.splitext(input_file_path)[0] + ".bin"

            def show_success_dialog(_min, _max, _del):
                def close_dlgconvert(e):
                    convertsuc.open = False
                    page.update()
                convertsuc = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.GREEN_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["result"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Column([
                        ft.Text(f"{lang['file_saved']}:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(output_path, size=12, width=450, color=ft.Colors.WHITE),
                    ], tight=True),
                    actions=[
                        ft.TextButton("OK", on_click=close_dlgconvert, style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: logging.info(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}"),
                )
                page.overlay.append(convertsuc)
                logging.info(f"Converted file saved to: {output_path}")
                page.update()

            try:
                _min, _max, _del = reverse_converter(input_file_path, output_path, json_data)
                show_success_dialog(_min, _max, _del)
            except struct.error as e:
                def close_banner(e):
                    errordialog.open = False
                    page.update()
                errordialog = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["struct_error"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=close_banner, style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton(lang["help"], on_click=lambda e: [close_banner(e), helpdialog(e)], style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                logging.error(f"struct.error occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(errordialog)
                page.update()
            except ZeroDivisionError as e:
                def close_zerbanner(e):
                    zererrordialog.open = False
                    page.update()
                zererrordialog = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_ACCENT_700,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["zerodiv_error"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=close_zerbanner, style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton(lang["opengit"], on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new"), style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                logging.error(f"ZeroDivisionError occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(zererrordialog)
                page.update()
            except ValueError as e:
                def close_valbanner(e):
                    valerrordialog.open = False
                    page.update()
                valerrordialog = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_ACCENT_700,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["unsupportedfile"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=close_valbanner, style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton(lang["opengit"], on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new"), style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                logging.error(f"ValueError occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(valerrordialog)
                page.update()
        else:
            def close_dlgpleaseselfile(e):
                plsselfile.open = False
                page.update()
            plsselfile = ft.AlertDialog(
                open=True,
                title=ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.RED),
                        ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.START,
                ),
                content=ft.Text(lang["plssel_file"]),
                actions=[
                    ft.TextButton("OK", on_click=close_dlgpleaseselfile)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(plsselfile)
            logging.warning("File is not selected!")
            page.update()

    def change_language(language_code):
        global lang
        lang = translations[language_code]
        LanguageManager.set_language(language_code)
        ui_components.lang = lang
        update_ui()
        show_language_dialog(None)

    def update_ui():
        top_bar.content.content.controls[0].controls[1].value = f"{page.title} {VERSION}"
        top_bar.content.content.controls[1].controls[0].tooltip = lang["min"]
        top_bar.content.content.controls[1].controls[1].tooltip = lang["exit"]
        file_name.label = lang["select_file"]
        select_button.text = lang["sel_button"]
        process_button.text = lang["convert_file"]
        toolbar_buttons['help'].content.tooltip = lang["help"]
        toolbar_buttons['language'].content.tooltip = lang["cnglang"]
        toolbar_buttons['theme'].tooltip = lang["toggletheme"]
        social_buttons['github'].content.tooltip = lang["github"]
        social_buttons['discord'].content.tooltip = lang["discord"]
        social_buttons['telegram'].content.tooltip = lang["telegram"]
        social_buttons['youtube'].content.tooltip = lang["youtube"]
        toolbar_buttons['mode'].tooltip = lang["modeswitch1"]
        json_field.label = lang["json"]
        select_json_button.text = lang["sel_button"]
        page.update()

    def show_language_dialog(e):
        lang_dialog = LanguageDialog(page, lang, change_language)
        lang_dialog.show()

    def toggle_theme(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        update_theme()

    def update_theme():
        colors = ThemeManager.get_theme_colors(page.theme_mode)
        
        toolbar_buttons['help'].content.icon_color = colors['icon_color']
        toolbar_buttons['language'].content.icon_color = colors['icon_color']
        toolbar_buttons['theme'].icon = colors['theme_icon']
        toolbar_buttons['theme'].icon_color = colors['icon_color']
        toolbar_buttons['mode'].icon_color = colors['icon_color']
        
        social_buttons['github'].content.color = colors['icon_color']
        social_buttons['discord'].content.color = colors['icon_color']
        social_buttons['telegram'].content.color = colors['icon_color']
        social_buttons['youtube'].content.color = colors['icon_color']
        
        title_image.src = colors['logo_src']
        icon_help_title.color = colors['text_color']
        text_help_title.color = colors['text_color']
        minimize_btn.icon_color = colors['icon_color']
        close_btn.icon_color = colors['icon_color']
        topbarico.src = colors['topbar_logo']
        json_field.border_color = colors['border_color']
        file_name.border_color = colors['border_color']
        select_button.style.color = colors['icon_color']
        process_button.style.color = colors['icon_color']
        vertext.color = colors['version_color']
        select_json_button.style.color = colors['icon_color']

        page.update()

    file_name = ft.TextField(
        value="",
        label=lang["select_file"],
        read_only=True,
        width=int(400 * scale_factor),
        label_style=ft.TextStyle(size=int(14 * scale_factor)),
        text_style=ft.TextStyle(size=int(14 * scale_factor)),
        content_padding=ft.padding.symmetric(
            horizontal=int(12 * scale_factor),
            vertical=int(8 * scale_factor)
        ),
        border_color="#46678F"
    )

    select_button = ft.ElevatedButton(
        text=lang["sel_button"],
        on_click=select_file,
        style=ft.ButtonStyle(
            color="#9ecaff",
            padding=ft.padding.symmetric(
                horizontal=int(20 * scale_factor),
                vertical=int(10 * scale_factor)
            ),
            text_style=ft.TextStyle(
                size=int(14 * scale_factor)
            )
        )
    )

    json_field = ft.TextField(
        value="",
        label=lang["json"],
        read_only=True,
        width=int(400 * scale_factor),
        label_style=ft.TextStyle(size=int(14 * scale_factor)),
        text_style=ft.TextStyle(size=int(14 * scale_factor)),
        content_padding=ft.padding.symmetric(
            horizontal=int(12 * scale_factor),
            vertical=int(8 * scale_factor)
        ),
        border_color="#46678F"
    )

    select_json_button = ft.ElevatedButton(
        text=lang["sel_button"],
        on_click=lambda _: json_picker.pick_files(),
        style=ft.ButtonStyle(
            color="#9ecaff",
            padding=ft.padding.symmetric(
                horizontal=int(20 * scale_factor),
                vertical=int(10 * scale_factor)
            ),
            text_style=ft.TextStyle(
                size=int(14 * scale_factor)
            )
        )
    )

    process_button = ft.ElevatedButton(
        text=lang["convert_file"],
        on_click=process_file,
        style=ft.ButtonStyle(
            color="#9ecaff",
            padding=ft.padding.symmetric(
                horizontal=int(30 * scale_factor),
                vertical=int(10 * scale_factor)
            ),
            text_style=ft.TextStyle(
                size=int(14 * scale_factor)
            )
        )
    )

    toolbar_buttons = ui_components.create_toolbar_buttons(
        on_help=helpdialog,
        on_language=show_language_dialog,
        on_theme=toggle_theme,
        on_mode_switch=lambda e: switch_to_ui(page),
        mode_tooltip_key="modeswitch1"
    )

    social_buttons = ui_components.create_social_buttons()

    toolbar_container = ui_components.create_toolbar_container(toolbar_buttons, social_buttons)

    version_container, vertext = ui_components.create_version_container(
        on_click=ui_components.show_version_info
    )

    page.add(
        ft.Column(
            [
                ft.Container(
                    ft.Column(
                        [file_name, select_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(int(1 * scale_factor)),
                ),
                ft.Container(height=int(20 * scale_factor)),

                ft.Container(
                    ft.Column(
                        [json_field, select_json_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(int(1 * scale_factor)),
                ),
                ft.Container(height=int(20 * scale_factor)),

                ft.Container(
                    ft.Column(
                        [
                            ft.Row([process_button], alignment=ft.MainAxisAlignment.CENTER)
                        ],
                        spacing=int(10 * scale_factor),
                    ),
                    padding=ft.padding.all(int(1 * scale_factor)),
                ),
                ft.Container(height=int(30 * scale_factor)),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    page.add(toolbar_container)
    page.add(version_container)

    update_theme()