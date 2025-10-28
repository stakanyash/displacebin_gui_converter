import flet as ft
import locale
from localization import translations
import os
from resources import get_asset_path
import logging
from datetime import datetime
import traceback
from screeninfo import get_monitors
from updater import check_for_updates, download_update
from converter import process_raw, process_png, struct, _write_metadata
import subprocess
import threading
import time

VERSION = "2.1"
BUILD = "[251028c]"
CHECKED_FOR_UPDATES = False

log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"dgc_{log_timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

locale.setlocale(locale.LC_ALL, '')
current_locale = locale.getlocale()[0]
system_lang = current_locale[:2] if current_locale else 'En'
lang = translations.get(system_lang, translations["En"])

class PageHelper:
    def __init__(self, page: ft.Page):
        self.page = page
        self.min_btn = ft.IconButton(icon=ft.Icons.REMOVE, icon_size=16, tooltip=lang["min"], on_click=self.minimize)
        self.close_btn = ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, tooltip=lang["exit"], on_click=self.close)

    def toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        self.page.update()

    def minimize(self, e):
        self.page.window.minimized = True
        self.page.update()

    def close(self, e):
        self.page.window.close()

def create_ui(page: ft.Page, lang_code="En"):
    global lang
    if lang_code in translations:
        lang = translations[lang_code]
    else:
        logging.warning(f"Unsupported language code '{lang_code}', defaulting to English.")
        lang = translations["En"]

    page.title = lang["title"]
    page.theme_mode = "dark"

    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    page.window.width = 580
    page.window.height = 680
    scale_factor = 1.0

    page.window.resizable = False
    page.window.maximizable = False
    page.window.minimizable = True
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.icon = get_asset_path('icon.ico')
    page.window.center()

    helper = PageHelper(page)

    def switch_to_reverse_ui(page: ft.Page):
        from reverse_ui import create_back_ui
        logging.info("Switched to \".raw/.png to .bin\" mode")
        page.clean()
        create_back_ui(page)

    logo = get_asset_path('icon.ico')

    btn_size = int(28 * scale_factor)
    icon_size = int(14 * scale_factor)
    
    minimize_btn = ft.IconButton(
        icon=ft.Icons.REMOVE,
        icon_size=icon_size,
        tooltip=lang["min"],
        on_click=helper.minimize,
        padding=int(4 * scale_factor),
        width=btn_size,
        height=btn_size,
    )

    close_btn = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_size=icon_size,
        tooltip=lang["exit"],
        on_click=helper.close,
        padding=int(4 * scale_factor),
        width=btn_size,
        height=btn_size,
    )

    topbarico = ft.Image(src=logo, width=16, height=16)

    top_bar = ft.Container(
        height=int(27 * scale_factor),
        bgcolor=ft.Colors.SURFACE,
        padding=ft.padding.symmetric(horizontal=int(8 * scale_factor)),
        content=ft.WindowDragArea(
            ft.Row(
                [
                    ft.Row(
                        [
                            topbarico,
                            ft.Text(
                                f"{lang['title']} {VERSION}",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            minimize_btn,
                            close_btn
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ),
    )

    page.add(top_bar)

    title_image = ft.Image(
        src=get_asset_path('logo.png'),
        fit=ft.ImageFit.CONTAIN
    )

    title_container = ft.Container(
        content=title_image,
        padding=ft.padding.only(
            top=int(10 * scale_factor),
            bottom=int(5 * scale_factor)
        ),
        alignment=ft.alignment.center,
        height=int(120 * scale_factor)
    )

    input_file_path = None
    dialog_open = False

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal input_file_path
        try:
            if e.files:
                input_file_path = e.files[0].path

            if not input_file_path.lower().endswith('.bin'):
                show_error_dialog(lang["error"], lang["wrong_extension"])
                file_name.value = ""
                input_file_path = None
                logging.error("Selected file is not .bin file!")
                page.update()
                return
        except AttributeError:
            logging.info("User closed file picker.")
            return

        file_name.value = input_file_path
        page.update()

    def show_error_dialog(title, message):
        def close_error_dialog(e):
            error_dialog.open = False
            page.update()

        error_dialog = ft.AlertDialog(
            open=True,
            bgcolor=ft.Colors.RED_900,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                    ft.Text(title, color=ft.Colors.WHITE)
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            content=ft.Text(message, color=ft.Colors.WHITE),
            actions=[ft.TextButton("OK", on_click=close_error_dialog, style=ft.ButtonStyle(color=ft.Colors.WHITE))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(error_dialog)
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def select_file(e):
        file_picker.pick_files()

    meta_dlg_titleicon = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=ft.Colors.WHITE)
    meta_dlg_titletext = ft.Text(lang["metadatainfo"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)

    def metadata_info_dialog(e):
        def close_dlgmeta(e):
            nonlocal dialog_open
            meta_dlg.open = False
            dialog_open = False
            page.update()

        meta_dlg = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    meta_dlg_titleicon,
                    meta_dlg_titletext
                ],
            ),
            content=ft.Text(lang["meta_text"]),
            actions=[
                ft.TextButton("OK", on_click=close_dlgmeta)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(meta_dlg)
        page.update()

    icon_help_title = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=ft.Colors.WHITE)
    text_help_title = ft.Text(lang["help"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)

    def helpdialog(e):
        def close_dlghelp(e):
            nonlocal dialog_open
            help_dlg.open = False
            dialog_open = False
            page.update()

        help_dlg = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    icon_help_title,
                    text_help_title,
                ],
            ),
            content=ft.Text(lang["help_text"]),
            actions=[
                ft.TextButton(lang["metadatainfo"], on_click=lambda e: [close_dlghelp(e), metadata_info_dialog(e)]),
                ft.TextButton("OK", on_click=close_dlghelp)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(help_dlg)
        page.update()

    file_name = ft.TextField(
        value="",
        label=lang["select_file"],
        read_only=True,
        border_color="#46678F",
        width=int(400 * scale_factor),
        label_style=ft.TextStyle(size=int(14 * scale_factor)),
        text_style=ft.TextStyle(size=int(14 * scale_factor)),
        content_padding=ft.padding.symmetric(
            horizontal=int(12 * scale_factor),
            vertical=int(8 * scale_factor)
        )
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
            overlay_color=ft.Colors.with_opacity(0.1, "#9ecaff"),
            text_style=ft.TextStyle(
                size=int(14 * scale_factor)
            )
        )
    )

    output_format_text = ft.Text(
        lang["select_format"],
        size=int(16 * scale_factor),
        text_align=ft.TextAlign.CENTER
    )

    output_format = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(
                label=".raw",
                value="RAW",
                scale=scale_factor,
                label_style=ft.TextStyle(
                    size=int(15 * scale_factor)
                )
            ),
            ft.Container(width=int(20 * scale_factor)),
            ft.Radio(
                label=".png",
                value="PNG",
                scale=scale_factor,
                label_style=ft.TextStyle(
                    size=int(15 * scale_factor),
                    weight=ft.FontWeight.W_500
                )
            )
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0)
    )

    output_size = ft.Container(
        content=ft.Dropdown(
            options=[
                ft.dropdown.Option(key="64", text="4x4"),
                ft.dropdown.Option(key="128", text="8x8"),
                ft.dropdown.Option(key="256", text="16x16"),
                ft.dropdown.Option(key="512", text="32x32"),
                ft.dropdown.Option(key="1024", text="64x64")
            ],
            label=lang["select_size"],
            label_style=ft.TextStyle(size=int(12 * scale_factor)),
            text_style=ft.TextStyle(size=int(12 * scale_factor)),
            border_color="#46678F",
            content_padding=ft.padding.symmetric(
                horizontal=int(12 * scale_factor),
                vertical=int(4 * scale_factor)
            ),
            width=int(350 * scale_factor)
        ),
        height=int(35 * scale_factor)
    )

    process_button = ft.ElevatedButton(
        text=lang["convert_file"], 
        on_click=lambda e: process_file(e), 
        style=ft.ButtonStyle(
            color="#9ecaff", 
            padding=ft.padding.only(
                left=int(16 * scale_factor),
                top=int(6 * scale_factor),
                right=int(16 * scale_factor),
                bottom=int(6 * scale_factor)
            ),
            overlay_color=ft.Colors.with_opacity(0.1, "#9ecaff"),
            text_style=ft.TextStyle(
                size=int(12 * scale_factor)
            )
        )
    )

    help_icon = ft.Icons.HELP_OUTLINE
    hover_icon = ft.Icons.HELP
    icon_size = int(24 * scale_factor)

    help_btn = ft.Container(
        content=ft.IconButton(
            icon=help_icon,
            on_click=helpdialog,
            icon_color="#9ecaff",
            tooltip=lang["help"],
            icon_size=icon_size,
            width=int(40 * scale_factor),
            height=int(40 * scale_factor)
        ),
        on_hover=lambda e: setattr(help_btn.content, 'icon', hover_icon if e.data == 'true' else help_icon)
    )

    language_icon = ft.Icons.LANGUAGE
    language_hover_icon = ft.Icons.LANGUAGE_OUTLINED

    language_btn = ft.Container(
        content=ft.IconButton(
            icon=language_icon,
            on_click=lambda e: show_language_dialog(e),
            icon_color="#9ecaff",
            tooltip=lang["cnglang"],
            icon_size=icon_size,
            width=int(40 * scale_factor),
            height=int(40 * scale_factor)
        ),
        on_hover=lambda e: setattr(language_btn.content, 'icon', language_hover_icon if e.data == 'true' else language_icon)
    )

    theme_icon = ft.Icons.BRIGHTNESS_MEDIUM
    theme_btn = ft.IconButton(
        icon=theme_icon,
        on_click=lambda e: toggle_theme(e),
        icon_color="#9ecaff",
        tooltip=lang["toggletheme"],
        icon_size=icon_size,
        width=int(40 * scale_factor),
        height=int(40 * scale_factor)
    )
    git_btn = ft.IconButton(
        content=ft.Image(
            src=get_asset_path('git.png'),
            width=icon_size,
            height=icon_size,
            color="#9ecaff",
            tooltip=lang["github"]
        ),
        on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter"),
    )

    dis_btn = ft.IconButton(
        content=ft.Image(
            src=get_asset_path('dis.png'),
            width=icon_size,
            height=icon_size,
            color="#9ecaff",
            tooltip=lang["discord"]
        ),
        on_click=lambda e: page.launch_url("https://discord.com/invite/Cd5GanuYud"),
    )

    tg_btn = ft.IconButton(
        content=ft.Image(
            src=get_asset_path('tg.png'),
            width=icon_size,
            height=icon_size,
            color="#9ecaff",
            tooltip=lang["telegram"]
        ),
        on_click=lambda e: page.launch_url("https://t.me/stakanyasher"),
    )

    yt_btn = ft.IconButton(
        content=ft.Image(
            src=get_asset_path('yt.png'),
            width=icon_size,
            height=icon_size,
            color="#9ecaff",
            tooltip=lang["youtube"]
        ),
        on_click=lambda e: page.launch_url("https://www.youtube.com/@stakanyash"),
    )

    rev_btn = ft.IconButton(
        icon=ft.Icons.SWAP_HORIZ,
        icon_size=icon_size,
        icon_color="#9ecaff",
        tooltip=lang["modeswitch2"],
        on_click=lambda e: switch_to_reverse_ui(page)
    )

    infoicon = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=ft.Colors.WHITE)

    content_column = ft.Container(
        content=ft.Column([
            ft.Text(
                spans=[
                    ft.TextSpan("powered by "),
                    ft.TextSpan("Python", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://www.python.org/"),
                    ft.TextSpan(", "),
                    ft.TextSpan("Flet", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://flet.dev/"),
                    ft.TextSpan(", "),
                    ft.TextSpan("Pillow", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://pillow.readthedocs.io/en/stable/"),
                    ft.TextSpan(", "),
                    ft.TextSpan("locale", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/locale.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("logging", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/logging.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("datetime", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/datetime.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("traceback", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/traceback.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("pathlib", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/pathlib.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("math", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/math.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("struct", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/struct.html"),
                    ft.TextSpan(", "),
                    ft.TextSpan("sys", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/sys.html"),
                ],
                selectable=True,
                no_wrap=False,
            ),
            ft.Text(
                spans=[
                    ft.TextSpan("Authors: "),
                    ft.TextSpan("stakan ", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://github.com/stakanyash"),
                    ft.TextSpan("(GUI), "),
                    ft.TextSpan("ThePlain ", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://github.com/ThePlain"),
                    ft.TextSpan("(conversion script)"),
                ],
                selectable=True,
                no_wrap=False,
            )
        ]),
        height=120,
        width=300,
        padding=10
    )

    def show_version_info(e):
        def close_dialog(e):
            dialog.open = False
            page.update()

        content_text = content_column

        dialog = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    infoicon,
                    ft.Text(lang["info"], style=ft.TextThemeStyle.TITLE_MEDIUM)
                ],
            ),
            content=content_text,
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        page.update()

    vertext = ft.Text(f"{VERSION} {BUILD}", size=10, color=ft.Colors.GREY)

    version_text = ft.GestureDetector(
        content=vertext,
        on_tap=show_version_info
    )

    version_container = ft.Container(
        content=version_text,
        alignment=ft.alignment.bottom_right,
        padding=ft.padding.only(right=10, bottom=10),
    )

    def process_file(e):
        if input_file_path and output_format.value and output_size.content.value:
            try:
                size = int(output_size.content.value)
            except Exception:
                try:
                    size = int(output_size.content.options[0].key)
                except Exception:
                    size = 64

            output_path = os.path.splitext(input_file_path)[0] + (".raw" if output_format.value == "RAW" else ".png")

            try:
                if output_format.value == "RAW":
                    _min, _max, _del, json_path = process_raw(input_file_path, output_path, size, True)
                else:
                    _min, _max, _del, json_path = process_png(input_file_path, output_path, size, True)

                def close_dlgconvert(e):
                    convertsuc.open = False
                    page.update()

                content_controls = [
                    ft.Text(f"{lang['file_saved']}:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(output_path, size=12, width=450, color=ft.Colors.WHITE),
                ]

                if json_path:
                    content_controls.extend([
                        ft.Text(f"{lang['meta_path']}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(json_path, size=12, width=450, color=ft.Colors.WHITE),
                    ])

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
                    content=ft.Column(content_controls, tight=True),
                    actions=[ft.TextButton("OK", on_click=close_dlgconvert, style=ft.ButtonStyle(color=ft.Colors.WHITE))],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: logging.info(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}"),
                )
                page.overlay.append(convertsuc)
                logging.info(f"Converted file saved to: {output_path}")
                page.update()

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
                        ft.TextButton("OK", on_click=lambda e: close_banner(e), style=ft.ButtonStyle(color=ft.Colors.WHITE)),
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
                        ft.TextButton("OK", on_click=lambda e: close_zerbanner(e), style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton(lang["opengit"], on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new"), style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                logging.error(f"ZeroDivisionError occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(zererrordialog)
                page.update()

        else:
            if not input_file_path or not output_format.value or not output_size.content.value:
                def close_dlgpleaseselfile(e):
                    nonlocal dialog_open
                    plsselfile.open = False
                    dialog_open = False
                    page.update()

                plsselfile = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.AMBER),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["plssel_file"], color=ft.Colors.WHITE),
                    actions=[ft.TextButton("OK", on_click=close_dlgpleaseselfile, style=ft.ButtonStyle(color=ft.Colors.WHITE))],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(plsselfile)
                logging.warning("File is not selected!")
                page.update()

    def change_language(language_code):
        global lang
        lang = translations[language_code]
        update_ui()
        show_language_dialog(None)

    def update_ui():
        try:
            top_bar.content.content.controls[0].controls[1].value = f"{lang['title']} {VERSION}"
            top_bar.content.content.controls[1].controls[0].tooltip = lang["min"]
            top_bar.content.content.controls[1].controls[1].tooltip = lang["exit"]
            helper.min_btn.tooltip = lang["min"]
            helper.close_btn.tooltip = lang["exit"]
            file_name.label = lang["select_file"]
            select_button.text = lang["sel_button"]
            output_format_text.value = lang["select_format"]
            output_format.content.controls[0].label = ".raw"
            output_format.content.controls[1].label = ".png"
            try:
                output_size.content.label = lang["select_size"]
            except Exception:
                pass
            process_button.text = lang["convert_file"]
            help_btn.content.tooltip = lang["help"]
            language_btn.content.tooltip = lang["cnglang"]
            theme_btn.tooltip = lang["toggletheme"]
            git_btn.content.tooltip = lang["github"]
            dis_btn.content.tooltip = lang["discord"]
            tg_btn.content.tooltip = lang["telegram"]
            yt_btn.content.tooltip = lang["youtube"]
            rev_btn.tooltip = lang["modeswitch2"]
            langdlgtext.value = lang["sel_lang"]
            text_help_title.value = lang["help"]
            page.update()
        except Exception as ex:
            logging.error("update_ui error: " + str(ex))

    lang_buttons = [
        ft.TextButton("Русский", on_click=lambda e: change_language("Ru"), style=ft.ButtonStyle(color="#9ecaff")),
        ft.TextButton("English", on_click=lambda e: change_language("En"), style=ft.ButtonStyle(color="#9ecaff")),
        ft.TextButton("Українська", on_click=lambda e: change_language("Uk"), style=ft.ButtonStyle(color="#9ecaff")),
        ft.TextButton("Беларуская", on_click=lambda e: change_language("Be"), style=ft.ButtonStyle(color="#9ecaff")),
        ft.TextButton("Polski", on_click=lambda e: change_language("Pl"), style=ft.ButtonStyle(color="#9ecaff"))
    ]

    langdlgicon = ft.Icon(ft.Icons.LANGUAGE, size=30, color=ft.Colors.WHITE)
    langdlgtext = ft.Text(lang["sel_lang"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)

    def show_language_dialog(e):
        def close_language_dialog(e):
            language_dialog.open = False
            page.update()

        language_dialog = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    langdlgicon,
                    langdlgtext
                ],
            ),
            content=ft.Container(
                content=ft.Column(
                    lang_buttons,
                    spacing=10,
                ),
                width=250,
                height=200,
            ),
            actions=[ft.TextButton(lang["cancel"], on_click=close_language_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(language_dialog)
        page.update()

    def toggle_theme(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        update_theme()

    def update_theme():
        if page.theme_mode == "dark":
            icon_color = "#9ecaff"
            logo_src = get_asset_path('logo.png')
            topbar_logo = get_asset_path('icon.ico')
            text_color = ft.Colors.WHITE
            theme_icon = ft.Icons.BRIGHTNESS_MEDIUM
            border_color = "#46678F"
            versioncolor = ft.Colors.GREY
        else:
            icon_color = "black"
            logo_src = get_asset_path('logo_white.png')
            topbar_logo = get_asset_path('iconblack.ico')
            text_color = ft.Colors.BLACK
            theme_icon = ft.Icons.BRIGHTNESS_3
            border_color = "#000000"
            versioncolor = ft.Colors.BLACK

        try:
            help_btn.content.icon_color = icon_color
            language_btn.content.icon_color = icon_color
            theme_btn.icon = theme_icon
            theme_btn.icon_color = icon_color
            git_btn.content.color = icon_color
            dis_btn.content.color = icon_color
            tg_btn.content.color = icon_color
            yt_btn.content.color = icon_color
            title_image.src = logo_src
            rev_btn.icon_color = icon_color
            icon_help_title.color = text_color
            text_help_title.color = text_color
            meta_dlg_titleicon.color = text_color
            meta_dlg_titletext.color = text_color
            minimize_btn.icon_color = icon_color
            close_btn.icon_color = icon_color
            topbarico.src = topbar_logo
            try:
                output_size.content.border_color = border_color
            except Exception:
                pass
            file_name.border_color = border_color
            select_button.style.color = icon_color
            process_button.style.color = icon_color
            vertext.color = versioncolor
            langdlgicon.color = icon_color
            langdlgtext.color = text_color
            infoicon.color = text_color

            for btn in lang_buttons:
                btn.style = ft.ButtonStyle(color=icon_color)

            page.update()
        except Exception as ex:
            logging.debug("update_theme partial: " + str(ex))

    main_content = ft.Container(
        content=ft.Column(
            [
                title_container,

                ft.Container(height=int(10 * scale_factor)),
                
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=file_name,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(height=int(10 * scale_factor)),
                            ft.Container(
                                content=select_button,
                                alignment=ft.alignment.center
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0
                    ),
                    padding=ft.padding.symmetric(
                        horizontal=int(20 * scale_factor),
                        vertical=int(10 * scale_factor)
                    ),
                ),
                
                ft.Container(height=int(20 * scale_factor)),
                
                ft.Container(
                    content=ft.Column(
                        [
                            output_format_text,
                            ft.Container(height=int(10 * scale_factor)),
                            output_format,
                            ft.Container(height=int(30 * scale_factor)),
                            ft.Container(
                                content=output_size,
                                width=int(300 * scale_factor),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(height=int(30 * scale_factor)),
                            process_button,
                            ft.Container(height=int(20 * scale_factor)),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=int(20 * scale_factor)),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        expand=True,
    )

    page.add(main_content)

    toolbar_container = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        help_btn,
                        ft.Container(width=int(10 * scale_factor)),
                        language_btn,
                        ft.Container(width=int(10 * scale_factor)),
                        theme_btn,
                        ft.Container(width=int(10 * scale_factor)),
                        rev_btn,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=int(10 * scale_factor)),
                ft.Row(
                    [
                        git_btn,
                        ft.Container(width=int(10 * scale_factor)),
                        dis_btn,
                        ft.Container(width=int(10 * scale_factor)),
                        tg_btn,
                        ft.Container(width=int(10 * scale_factor)),
                        yt_btn,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(bottom=int(10 * scale_factor)),
    )

    page.add(toolbar_container)
    page.add(version_container)

    def check_updates():
        try:
            update_info = check_for_updates(VERSION)
            
            if update_info.get('update_available'):
                def close_update_dialog(e):
                    update_dlg.open = False
                    page.update()
                    logging.info("Update dialog closed by user")
                    
                def start_update(e):
                    try:
                        update_dlg.open = False
                        page.update()
                        logging.info("Starting update process")

                        download_cancelled = False
                        
                        def close_download_dialog(e):
                            nonlocal download_cancelled
                            download_cancelled = True
                            download_dlg.open = False
                            page.update()
                            logging.info("Download cancelled by user")

                        progress_bar = ft.ProgressBar(width=400, color="PRIMARY")
                        progress_text = ft.Text("0.0mb/0.0mb", size=12, color=ft.Colors.GREY_500)
                        
                        download_dlg = ft.AlertDialog(
                            modal=True,
                            title=ft.Row([
                                ft.Icon(ft.Icons.DOWNLOAD, color=ft.Colors.BLUE_400),
                                ft.Text(lang["downloading"]),
                            ]),
                            content=ft.Column([
                                progress_bar,
                                ft.Container(
                                    content=progress_text,
                                    alignment=ft.alignment.center_right,
                                    padding=ft.padding.only(top=5)
                                )
                            ], tight=True),
                            actions=[
                                ft.TextButton(
                                    lang["cancel"],
                                    on_click=close_download_dialog,
                                )
                            ],
                            actions_alignment=ft.MainAxisAlignment.END,
                        )

                        page.overlay.append(download_dlg)
                        download_dlg.open = True
                        page.update()
                        
                        def update_progress(value, current_size, total_size, cancel_fn):
                            if download_cancelled:
                                cancel_fn()
                            progress_bar.value = value / 100
                            progress_text.value = f"{current_size:.1f}mb/{total_size:.1f}mb"
                            page.update()
                        
                        try:
                            save_path = download_update(update_info['download_url'], update_progress)
                            if save_path:
                                download_dlg.open = False
                                logging.info("Download completed successfully")
                                
                                success_dlg = ft.AlertDialog(
                                    title=ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400),
                                        ft.Text(lang["update_downloaded"]),
                                    ]),
                                    content=ft.Text(lang["restart"]),
                                )
                                page.overlay.append(success_dlg)
                                success_dlg.open = True
                                page.update()
                                
                                logging.info("Preparing to restart application")
                                
                                def restart_app():
                                    try:
                                        time.sleep(1)
                                        logging.info(f"Starting new version from: {save_path}")
                                        subprocess.Popen([save_path])
                                        logging.info("New version started successfully")
                                        page.window.destroy()
                                    except Exception as e:
                                        logging.error(f"Failed to start new version: {e}")
                                
                                threading.Thread(target=restart_app, daemon=True).start()
                                
                        except Exception as e:
                            logging.error(f"Update error: {str(e)}")
                            if not download_cancelled:
                                download_dlg.content = ft.Column([
                                    ft.Text("Error downloading update:", color=ft.Colors.RED_400),
                                    ft.Text(str(e), size=12),
                                ])
                                download_dlg.actions = [
                                    ft.TextButton("OK", on_click=lambda _: close_download_dialog(None))
                                ]
                                page.update()
                    except Exception as e:
                        logging.error(f"Error in start_update: {str(e)}")
                        page.update()

                changelog_text = update_info['description']
                changelog_text = changelog_text.replace('###', '')
                changelog_text = changelog_text.replace('##', '')
                changelog_text = changelog_text.replace('#', '')
                changelog_text = changelog_text.replace('*', '')
                changelog_text = changelog_text.replace('`', '')
                changelog_text = changelog_text.replace('>', '')
                changelog_text = changelog_text.replace('-', '•')
                changelog_text = '\n'.join(line.strip() for line in changelog_text.split('\n') if line.strip())
                
                update_dlg = ft.AlertDialog(
                    title=ft.Row([
                        ft.Icon(ft.Icons.SYSTEM_UPDATE, color=ft.Colors.BLUE_400),
                        ft.Text(lang["update_available"]),
                    ]),
                    content=ft.Container(
                        width=550,
                        content=ft.Column([
                            ft.Text(
                                f"{lang['version_for_download']} {update_info['version']}",
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Divider(),
                            ft.Container(
                                content=ft.ListView(
                                    [
                                        ft.Text(
                                            changelog_text,
                                            selectable=True,
                                            size=14,
                                        )
                                    ],
                                    spacing=10,
                                    height=350,
                                ),
                                padding=10,
                                height=350,
                            )
                        ], tight=True, spacing=10),
                    ),
                    actions=[
                        ft.TextButton(
                            lang["update_now"],
                            on_click=start_update,
                            style=ft.ButtonStyle(color=ft.Colors.BLUE_400)
                        ),
                        ft.TextButton(
                            lang["cancel"],
                            on_click=close_update_dialog
                        )
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                page.overlay.append(update_dlg)
                update_dlg.open = True
                logging.info(f"{update_info['version']} update available.")
                page.update()
        except Exception as e:
            logging.error(f"Error checking for updates: {str(e)}")

    global CHECKED_FOR_UPDATES

    if not CHECKED_FOR_UPDATES:
        check_updates()
        CHECKED_FOR_UPDATES = True

    update_theme()
    update_ui()