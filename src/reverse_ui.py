import flet as ft
import locale
from localization import translations
from reverse_converter import reverse_converter, struct
import os
from resources import get_asset_path
import logging
from datetime import datetime
import traceback

VERSION = "2.0"

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

def create_back_ui(page: ft.Page):
    global lang

    page.title = lang["title"]
    page.theme_mode = "dark"
    page.window.maximizable = False
    page.window.height = 810
    page.window.width = 640
    page.window.resizable = False
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.icon = get_asset_path('icon.ico')

    helper = PageHelper(page)
    logging.info("Switched to \".raw to .bin\" mode")

    def switch_to_ui(page: ft.Page):
        from ui import create_ui
        page.clean()
        logging.info("Switched to \".bin to .raw/.png\" mode")
        create_ui(page)

    def update_theme():
        if page.theme_mode == "dark":
            icon_color = "#9ecaff"
            logo_src = get_asset_path('logo.png')
            theme_icon = ft.Icons.BRIGHTNESS_MEDIUM
            topbar_logo = get_asset_path('icon.ico')
            text_color = ft.Colors.WHITE
            border_color = "#46678F"
            versioncolor = ft.Colors.GREY
        else:
            icon_color = "black"
            logo_src = get_asset_path('logo_white.png')
            theme_icon = ft.Icons.BRIGHTNESS_3
            topbar_logo = get_asset_path('iconblack.ico')
            text_color = ft.Colors.BLACK
            border_color = "#000000"
            versioncolor = ft.Colors.BLACK

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
        minimize_btn.icon_color = icon_color
        close_btn.icon_color = icon_color
        topbarico.src = topbar_logo
        icon_help_title.color = text_color
        text_help_title.color = text_color
        json_field.border_color = border_color
        select_button.style.color = icon_color
        process_button.style.color = icon_color
        vertext.color = versioncolor
        select_json_button.style.color = icon_color
        langdlgicon.color = icon_color
        langdlgtext.color = text_color
        infoicon.color = text_color

        for btn in lang_buttons:
            btn.style = ft.ButtonStyle(color=icon_color)

        page.update()

    logo = get_asset_path('icon.ico')

    minimize_btn = ft.IconButton(
        icon=ft.Icons.REMOVE,
        icon_size=14,
        tooltip=lang["min"],
        on_click=helper.minimize,
        padding=4,
        width=28,
        height=27,
    )

    close_btn = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_size=14,
        tooltip=lang["exit"],
        on_click=helper.close,
        padding=4,
        width=28,
        height=27,
    )

    topbarico = ft.Image(src=logo, width=16, height=16)

    top_bar = ft.Container(
        height=27,
        bgcolor=ft.Colors.SURFACE,
        padding=ft.padding.symmetric(horizontal=8),
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
        width=900,
        height=155,
        fit=ft.ImageFit.CONTAIN
    )

    title_container = ft.Container(
        content=title_image,
        padding=ft.padding.all(10),
        alignment=ft.alignment.center
    )

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

                if file_ext not in [".raw", ".png"]:
                    show_error_dialog(lang["error"], lang["wrong_extension_reverse"])
                    file_name.value = ""
                    input_file_path = None
                    logging.error("Selected file is not .raw!")
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

    json_file_path = None  # переменная для хранения пути к JSON
    json_data = {}  # переменная для хранения содержимого JSON

    def on_json_selected(e: ft.FilePickerResultEvent):
        nonlocal json_file_path, json_data
        if e.files:
            json_file_path = e.files[0].path
            _, ext = os.path.splitext(json_file_path)
            if ext.lower() != ".json":
                show_error_dialog(lang["error"], lang["wrong_extension_json"])
                json_file_path = None
                json_field.value = ""
                json_data = {}
                page.update()
                return

            try:
                import json
                with open(json_file_path, "r") as f:
                    json_data = json.load(f)
                json_field.value = json_file_path
                page.update()
            except Exception as ex:
                logging.error(f"Ошибка чтения JSON: {ex}")
                show_error_dialog(lang["error"], lang["invalid_json_metadata"])
                json_file_path = None
                json_data = {}
                json_field.value = ""
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
            global dialog_open
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
            content=ft.Text(lang["reversehelp_text"]),
            actions=[
                ft.TextButton("OK", on_click=close_dlghelp)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print(lang["help_print"]),
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
                actions=[ft.TextButton("OK", on_click=close_invalid_json, style=ft.ButtonStyle(color=ft.Colors.WHITE))],
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
                    actions=[ft.TextButton("OK", on_click=close_invalid_input, style=ft.ButtonStyle(color=ft.Colors.WHITE))],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(invalid_input_dialog)
                page.update()
                return

            # Выходной файл всегда будет .bin
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
                    actions=[ft.TextButton("OK", on_click=close_dlgconvert, style=ft.ButtonStyle(color=ft.Colors.WHITE))],
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
                        ft.TextButton(lang["opengit"], on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new"),   style=ft.ButtonStyle(color=ft.Colors.WHITE))
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
                        ft.TextButton(lang["opengit"], on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new"),   style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                logging.error(f"ValueError occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(valerrordialog)
                page.update()
        else:
            def close_dlgpleaseselfile(e):
                global dialog_open
                plsselfile.open = False
                dialog_open = False
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
                actions=[ft.TextButton("OK", on_click=close_dlgpleaseselfile)],
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
        top_bar.content.content.controls[0].controls[1].value = f"{lang['title']} {VERSION}"
        top_bar.content.content.controls[1].controls[0].tooltip = lang["min"]
        top_bar.content.content.controls[1].controls[1].tooltip = lang["exit"]
        helper.min_btn.tooltip = lang["min"]
        helper.close_btn.tooltip = lang["exit"]
        file_name.label = lang["select_file"]
        select_button.text = lang["sel_button"]
        process_button.text = lang["convert_file"]
        help_btn.content.tooltip = lang["help"]
        language_btn.content.tooltip = lang["cnglang"]
        theme_btn.tooltip = lang["toggletheme"]
        git_btn.content.tooltip = lang["github"]
        dis_btn.content.tooltip = lang["discord"]
        tg_btn.content.tooltip = lang["telegram"]
        yt_btn.content.tooltip = lang["youtube"]
        rev_btn.tooltip = lang["modeswitch1"]
        json_field.label = lang["json"]
        select_json_button.text = lang["sel_button"]
        langdlgtext.value = lang["sel_lang"]
        page.update()

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

    file_name = ft.TextField(
        value="",
        label=lang["select_file"],
        read_only=True,
        width=550,
        border_color="#46678F"
    )

    select_button = ft.ElevatedButton(lang["sel_button"], on_click=select_file, style=ft.ButtonStyle(color="#9ecaff", padding=ft.padding.only(left=20, top=10, right=20, bottom=10)))

    json_field = ft.TextField(
        value="",
        label=lang["json"],
        read_only=True,
        width=550,
        border_color="#46678F"
    )

    select_json_button = ft.ElevatedButton(lang["sel_button"], on_click=lambda _: json_picker.pick_files(), style=ft.ButtonStyle(color="#9ecaff", padding=ft.padding.only(left=20, top=10, right=20, bottom=10)))

    process_button = ft.ElevatedButton(lang["convert_file"], on_click=process_file, style=ft.ButtonStyle(color="#9ecaff", padding=ft.padding.only(left=30, top=10, right=30, bottom=10)))

    help_icon = ft.Icons.HELP_OUTLINE
    hover_icon = ft.Icons.HELP

    help_btn = ft.Container(
        content=ft.IconButton(
            icon=help_icon,
            on_click=helpdialog,
            icon_color="#9ecaff",
            tooltip=lang["help"]
        ),
        on_hover=lambda e: setattr(help_btn.content, 'icon', hover_icon if e.data == 'true' else help_icon)
    )

    language_icon = ft.Icons.LANGUAGE
    language_hover_icon = ft.Icons.LANGUAGE_OUTLINED

    language_btn = ft.Container(
        content=ft.IconButton(
            icon=language_icon,
            on_click=show_language_dialog,
            icon_color="#9ecaff",
            tooltip=lang["cnglang"]
        ),
        on_hover=lambda e: setattr(language_btn.content, 'icon', language_hover_icon if e.data == 'true' else language_icon)
    )

    theme_icon = ft.Icons.BRIGHTNESS_MEDIUM
    theme_btn = ft.IconButton(
        icon=theme_icon,
        on_click=toggle_theme,
        icon_color="#9ecaff",
        tooltip=lang["toggletheme"]
    )

    git_btn = ft.IconButton(
        content=ft.Image(src=get_asset_path('git.png'), width=24, height=24, color="#9ecaff", tooltip=lang["github"]),
        on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter"),
    )

    dis_btn = ft.IconButton(
        content=ft.Image(src=get_asset_path('dis.png'), width=24, height=24, color="#9ecaff", tooltip=lang["discord"]),
        on_click=lambda e: page.launch_url("https://discord.com/invite/Cd5GanuYud"),
    )

    tg_btn = ft.IconButton(
        content=ft.Image(src=get_asset_path('tg.png'), width=24, height=24, color="#9ecaff", tooltip=lang["telegram"]),
        on_click=lambda e: page.launch_url("https://t.me/stakanyasher"),
    )

    yt_btn = ft.IconButton(
        content=ft.Image(src=get_asset_path('yt.png'), width=24, height=24, color="#9ecaff", tooltip=lang["youtube"]),
        on_click=lambda e: page.launch_url("https://www.youtube.com/@stakanyash"),
    )

    rev_btn = ft.IconButton(
        icon=ft.Icons.SWAP_HORIZONTAL_CIRCLE_OUTLINED,
        icon_size=24,
        icon_color="#9ecaff",
        tooltip=lang["modeswitch1"],
        on_click=lambda e: switch_to_ui(page)
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
                    padding=ft.padding.all(2),
                ),
                ft.Divider(color="transparent"),
                ft.Container(height=0),

                ft.Container(
                    ft.Column(
                        [json_field, select_json_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(2),
                ),
                ft.Divider(color="transparent"),
                ft.Container(height=11.5),

                ft.Container(
                    ft.Column(
                        [
                            ft.Row([process_button], alignment=ft.MainAxisAlignment.CENTER)
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.all(2),
                ),
                ft.Container(height=85),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    page.add(
        ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            help_btn,
                            ft.Container(width=5),
                            language_btn,
                            ft.Container(width=5),
                            theme_btn,
                            ft.Container(width=5),
                            rev_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    ft.Container(height=1),
                    ft.Row(
                        [
                            git_btn,
                            ft.Container(width=5),
                            dis_btn,
                            ft.Container(width=5),
                            tg_btn,
                            ft.Container(width=5),
                            yt_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                spacing=2,
            ),
            padding=ft.padding.all(2),
        )
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
        height=80,
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

    vertext = ft.Text("Python 2.0 [250603d]", size=10, color=ft.Colors.GREY)
    
    version_text = ft.GestureDetector(
        content=vertext,
        on_tap=show_version_info
    )

    version_container = ft.Container(
        content=version_text,
        alignment=ft.alignment.bottom_right,
        padding=ft.padding.only(right=10, bottom=10),
    )

    page.add(version_container)

    update_theme()