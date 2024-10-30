import flet as ft
from converter import process_raw, process_png
from localization import lang

def create_ui(page: ft.Page):
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
    file_name = ft.TextField(value="", label=lang["select_file"], read_only=True, width=550)
    
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

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def select_file(e):
        file_picker.pick_files()

    def show_error_dialog(title, message):
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: error_dialog.close())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = error_dialog
        error_dialog.open = True
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

                show_result_dialog(f"{lang['file_saved']}: {output_path}\n")
            except struct.error:
                show_error_dialog(lang["error"], lang["struct_error"])
        else:
            show_error_dialog(lang["error"], lang["plssel_file"])

    def show_result_dialog(result_text):
        dialog = ft.AlertDialog(
            title=ft.Text(lang["conv_result"]),
            content=ft.Text(result_text),
            actions=[ft.TextButton("OK", on_click=lambda e: dialog.close())],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    output_format = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(label=".raw", value="RAW"),
            ft.Radio(label=".png", value="PNG")
        ], alignment=ft.MainAxisAlignment.CENTER)
    )

    output_size = ft.Dropdown(
        width=400,
        options=[ft.dropdown.Option("512"), ft.dropdown.Option("1024")],
        label=lang["select_size"],
    )

    process_button = ft.ElevatedButton(lang["convert_file"], on_click=process_file)

    page.add(
        ft.Column(
            [
                ft.Container(
                    ft.Column(
                        [file_name, ft.ElevatedButton(lang["sel_button"], on_click=select_file)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(10),
                ),
                ft.Divider(color="transparent"),
                ft.Container(
                    ft.Column(
                        [
                            ft.Text(lang["select_format"], size=16, text_align=ft.TextAlign.CENTER),
                            output_format,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(10),
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
                    padding=ft.padding.all(10),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
