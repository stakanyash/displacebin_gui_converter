import flet as ft
import locale
from localization import translations
from converter import process_raw, process_png, struct
import os
from resources import get_asset_path
import logging
from datetime import datetime
import traceback

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

def create_ui(page: ft.Page):
    global lang

    page.title = lang["title"]
    page.theme_mode = "dark"
    page.window.maximizable = False
    page.window.height = 800
    page.window.width = 640
    page.window.resizable = False
    page.window.icon = get_asset_path('icon.ico')

    def update_theme():
        if page.theme_mode == "dark":
            icon_color = "#9ecaff"
            logo_src = get_asset_path('logo.png')
            theme_icon = ft.icons.BRIGHTNESS_MEDIUM
        else:
            icon_color = "black"
            logo_src = get_asset_path('logo_white.png')
            theme_icon = ft.icons.BRIGHTNESS_3

        help_btn.content.icon_color = icon_color
        language_btn.content.icon_color = icon_color
        theme_btn.icon = theme_icon
        theme_btn.icon_color = icon_color
        git_btn.content.color = icon_color
        dis_btn.content.color = icon_color
        tg_btn.content.color = icon_color
        yt_btn.content.color = icon_color
        title_image.src = logo_src
        page.update()

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
        if e.files:
            input_file_path = e.files[0].path

        if not input_file_path.lower().endswith('.bin'):
            show_error_dialog(lang["error"], lang["wrong_extension"])
            file_name.value = ""
            input_file_path = None
            logging.error("Selected file is not .bin file!")
            page.update()
            return

        file_name.value = input_file_path
        page.update()

    def show_error_dialog(title, message):
        def close_error_dialog(e):
            error_dialog.open = False
            page.update()

        error_dialog = ft.AlertDialog(
            open=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_error_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(error_dialog)
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def select_file(e):
        file_picker.pick_files()

    def helpdialog(e):
        def close_dlghelp(e):
            global dialog_open
            help_dlg.open = False
            dialog_open = False
            page.update()

        help_dlg = ft.AlertDialog(
            open=True,
            title=ft.Text(lang["help"]),
            content=ft.Text(lang["help_text"]),
            actions=[
                ft.TextButton("OK", on_click=close_dlghelp)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print(lang["help_print"]),
        )
        page.overlay.append(help_dlg)
        page.update()

    def process_file(e):
        if input_file_path and output_format.value and output_size.value:
            size = int(output_size.value)
            output_path = os.path.splitext(input_file_path)[0] + (".raw" if output_format.value == "RAW" else ".png")

            try:
                if output_format.value == "RAW":
                    _min, _max, _del = process_raw(input_file_path, output_path, size)
                else:
                    _min, _max, _del = process_png(input_file_path, output_path, size)

                def close_dlgconvert(e):
                    convertsuc.open = False
                    page.update()

                convertsuc = ft.AlertDialog(
                    open=True,
                    title=ft.Text(lang["result"]),
                    content=ft.Text(f"{lang['file_saved']}: {output_path}\n"),
                    actions=[ft.TextButton("OK", on_click=close_dlgconvert)],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: print(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}"),
                )
                page.overlay.append(convertsuc)
                logging.info(f"Converted file saved to: {output_path}")
                page.update()

            except struct.error as e:
                def close_banner(e):
                    errorbanner.open = False
                    page.update()

                errorbanner = ft.Banner(
                    open=True,
                    bgcolor=ft.colors.RED_700,
                    leading=ft.Icon(ft.icons.WARNING, size=35, color=ft.colors.AMBER),
                    content=ft.Text(lang["struct_error"]),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: close_banner(e)),
                        ft.TextButton(lang["help"], on_click=lambda e: [close_banner(e), helpdialog(e)])
                    ]
                )
                logging.error(f"struct.error occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(errorbanner)
                page.update()

        else:
            if not input_file_path or not output_format.value or not output_size.value:
                def close_dlgpleaseselfile(e):
                    global dialog_open
                    plsselfile.open = False
                    dialog_open = False
                    page.update()

                plsselfile = ft.AlertDialog(
                    open=True,
                    title=ft.Text(lang["error"]),
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
        file_name.label = lang["select_file"]
        select_button.text = lang["sel_button"]
        output_format_text.value = lang["select_format"]
        output_format.content.controls[0].label = ".raw"
        output_format.content.controls[1].label = ".png"
        output_size.label = lang["select_size"]
        process_button.text = lang["convert_file"]
        help_btn.content.tooltip = lang["help"]
        language_btn.content.tooltip = lang["cnglang"]
        theme_btn.tooltip = lang["toggletheme"]
        git_btn.content.tooltip = lang["github"]
        dis_btn.content.tooltip = lang["discord"]
        tg_btn.content.tooltip = lang["telegram"]
        yt_btn.content.tooltip = lang["youtube"]
        page.update()

    def show_language_dialog(e):
        def close_language_dialog(e):
            language_dialog.open = False
            page.update()

        language_dialog = ft.AlertDialog(
            open=True,
            title=ft.Text(lang["sel_lang"]),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.TextButton("Русский", on_click=lambda e: change_language("Ru")),
                        ft.TextButton("English", on_click=lambda e: change_language("En")),
                        ft.TextButton("Українська", on_click=lambda e: change_language("Uk")),
                        ft.TextButton("Беларуская", on_click=lambda e: change_language("Be")),
                        ft.TextButton("Polski", on_click=lambda e: change_language("Pl"))
                    ],
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
        width=550
    )

    select_button = ft.ElevatedButton(lang["sel_button"], on_click=select_file)

    output_format_text = ft.Text(
        lang["select_format"],
        size=16,
        text_align=ft.TextAlign.CENTER
    )

    output_format = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(label=".raw", value="RAW"),
            ft.Radio(label=".png", value="PNG")
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    output_size = ft.Dropdown(
        width=400,
        options=[
            ft.dropdown.Option(key="64", text="4x4"),
            ft.dropdown.Option(key="128", text="8x8"),
            ft.dropdown.Option(key="256", text="16x16"),
            ft.dropdown.Option(key="512", text="32x32"),
            ft.dropdown.Option(key="1024", text="64x64")
        ],
        label=lang["select_size"],
        label_style=ft.TextStyle(size=13)
    )

    process_button = ft.ElevatedButton(lang["convert_file"], on_click=process_file)

    help_icon = ft.icons.HELP_OUTLINE
    hover_icon = ft.icons.HELP

    help_btn = ft.Container(
        content=ft.IconButton(
            icon=help_icon,
            on_click=helpdialog,
            icon_color="#9ecaff",
            tooltip=lang["help"]
        ),
        on_hover=lambda e: setattr(help_btn.content, 'icon', hover_icon if e.data == 'true' else help_icon)
    )

    language_icon = ft.icons.LANGUAGE
    language_hover_icon = ft.icons.LANGUAGE_OUTLINED

    language_btn = ft.Container(
        content=ft.IconButton(
            icon=language_icon,
            on_click=show_language_dialog,
            icon_color="#9ecaff",
            tooltip=lang["cnglang"]
        ),
        on_hover=lambda e: setattr(language_btn.content, 'icon', language_hover_icon if e.data == 'true' else language_icon)
    )

    theme_icon = ft.icons.BRIGHTNESS_MEDIUM
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

                ft.Container(
                    ft.Column(
                        [
                            output_format_text,
                            output_format,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(2),
                ),
                ft.Divider(color="transparent"),

                ft.Container(
                    ft.Column(
                        [
                            ft.Row([output_size], alignment=ft.MainAxisAlignment.CENTER),
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

    version_text = ft.Text(
        "Python 1.2.6 [250320]",
        size=10,
        color=ft.colors.GREY,
    )

    version_container = ft.Container(
        content=version_text,
        alignment=ft.alignment.bottom_right,
        padding=ft.padding.only(right=10, bottom=10),
    )

    page.add(version_container)


    update_theme()
