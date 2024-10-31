import flet as ft
import locale
from localization import translations
from converter import process_raw, process_png, struct
import os

system_lang = locale.getdefaultlocale()[0][:2]
lang = translations.get(system_lang, translations["en"])

def create_ui(page: ft.Page):
    global lang

    page.title = lang["title"]
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = "dark"
    page.window_maximizable = False
    page.window_height = 680
    page.window_width = 640
    page.window_resizable = False

    title_text = ft.Text(
        lang["title"],
        size=24,
        weight="bold",
        text_align=ft.TextAlign.CENTER
    )

    title_container = ft.Container(
        content=title_text,
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
            input_file_path = None
            return

        file_name.value = input_file_path
        page.update()

    def show_error_dialog(title, message):
        def close_error_dialog(e):
            error_dialog.open = False
            page.update()

        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_error_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = error_dialog
        error_dialog.open = True
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def select_file(e):
        file_picker.pick_files()

    def show_result_dialog(result_text):
        dialog = ft.AlertDialog(
            title=ft.Text(lang["conv_result"]),
            content=ft.Text(result_text),
            actions=[ft.TextButton("OK", on_click=lambda e: page.dialog.close())],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def helpdialog(e):
        def close_dlghelp(e):
            global dialog_open
            help_dlg.open = False
            dialog_open = False
            page.update()

        help_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(lang["help"]),
            content=ft.Text(lang["help_text"]),
            actions=[
                ft.TextButton("OK", on_click=close_dlghelp)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print(lang["help_print"]),
        )
        page.dialog = help_dlg
        help_dlg.open = True
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
                    modal=True,
                    title=ft.Text(lang["result"]),
                    content=ft.Text(f"{lang['file_saved']}: {output_path}\n"),
                    actions=[ft.TextButton("OK", on_click=close_dlgconvert)],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: print(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}"),
                )
                page.dialog = convertsuc
                convertsuc.open = True
                page.update()

            except struct.error as e:
                def close_dlg_error(e):
                    error_dialog.open = False
                    page.update()

                error_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(lang["error"]),
                    content=ft.Text(lang["struct_error"]),
                    actions=[ft.TextButton("OK", on_click=close_dlg_error)],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: print(f"Error: {str(e)}"),
                )
                page.dialog = error_dialog
                error_dialog.open = True
                page.update()

        else:
            if not input_file_path or not output_format.value or not output_size.value:
                def close_dlgpleaseselfile(e):
                    global dialog_open
                    plsselfile.open = False
                    dialog_open = False
                    page.update()

                plsselfile = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(lang["error"]),
                    content=ft.Text(lang["plssel_file"]),
                    actions=[ft.TextButton("OK", on_click=close_dlgpleaseselfile)],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.dialog = plsselfile
                plsselfile.open = True
                page.update()

    def change_language(e):
        global lang
        lang = translations[language_selector.value]
        update_ui()

    def update_ui():
        title_text.value = lang["title"]
        file_name.label = lang["select_file"]
        select_button.text = lang["sel_button"]
        output_format_text.value = lang["select_format"]
        output_format.content.controls[0].label = ".raw"
        output_format.content.controls[1].label = ".png"
        output_size.label = lang["select_size"]
        process_button.text = lang["convert_file"]
        help_btn.tooltip = lang["help"]
        language_selector.label = lang["sel_lang"]
        page.update()

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
            ft.dropdown.Option("512"),
            ft.dropdown.Option("1024")
        ],
        label=lang["select_size"],
        label_style=ft.TextStyle(size=13)
    )

    process_button = ft.ElevatedButton(lang["convert_file"], on_click=process_file)

    help_icon = ft.icons.HELP_OUTLINE
    hover_icon = ft.icons.HELP

    help_btn = ft.IconButton(
        icon=help_icon,
        on_click=helpdialog,
        icon_color="#9ecaff"
    )

    def change_icon(e):
        if e.data == "true":
            help_btn.icon = hover_icon
        else:
            help_btn.icon = help_icon
        page.update()

    help_btn_container = ft.Container(
        content=help_btn,
        on_hover=change_icon,
        alignment=ft.alignment.center,
        padding=ft.padding.only(left=0, right=0, top=5, bottom=5)
    )

    language_selector = ft.Dropdown(
        width=200,
        options=[
            ft.dropdown.Option("ru", "Русский"),
            ft.dropdown.Option("en", "English"),
            ft.dropdown.Option("uk", "Українська")
        ],
        label=lang["sel_lang"],
        on_change=change_language
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
            ft.Row(
                [
                    help_btn_container,
                    ft.Container(width=5),
                    language_selector,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            padding=ft.padding.all(2),
        )
    )
