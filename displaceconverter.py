import flet as ft
import struct
from PIL import Image
import os
import locale

translations = {
    "en": {
        "title": "displace.bin converter",
        "error": "Error",
        "sel_file": "Please select a file",
        "select_file": "Selected file",
        "file_saved": "File saved as",
        "conv_result": "Processing result",
        "result": "Result",
        "plssel_file": "Please select a file, format, and size.",
        "sel_button": "Select file",
        "select_size": "Select size",
        "convert_file": "Convert file",
        "select_format": "Select output file format:",
        "help": "Help",
        "help_text": (
            "This program will help you to convert displace.bin of your map\n"
            "to .raw or .png format.\n"
            "\n"
            "To convert the file, you need to select the displace.bin file in the map folder, select the format (raw or png), and select the map size (512 or 1024).\n"
            "\n"
            "After that, click the 'Convert file' button. In case of success, you will see a success message\n"
            "and a file in the format of your choice will appear in the folder.\n"
            "\n"
            "Map size reference: 512 - the size of Krai. 1024 - the size of Vaterland, Vahat\n"
            "\n"
            "Program author: stakan\n"
            "Convert script author: ThePlain\n"
            "\n"
            "Created for the convenience of modders in the Deus Ex Machina community :)"
        ),
        "help_print": "Help dialog window is closed",
        "struct_error": (
            "An error occurred while converting the file.\n"
            "\n"
            "Please check the selected map size (valid values: 512 or 1024).\n"
            "\n"
            "For additional information, please open the help section."
        ),
        "wrong_extension": "Wrong file extension! Please select a .bin file!"
    },
    "ru": {
        "title": "displace.bin конвертер",
        "error": "Ошибка",
        "sel_file": "Пожалуйста, выберите файл",
        "select_file": "Выбранный файл",
        "file_saved": "Файл сохранён как",
        "conv_result": "Результат обработки",
        "result": "Результат",
        "plssel_file": "Пожалуйста, выберите файл, формат и размер.",
        "sel_button": "Выбрать файл",
        "select_size": "Выберите размер",
        "convert_file": "Преобразовать файл",
        "select_format": "Выберите формат выходного файла:",
        "help": "Помощь",
        "help_text": (
            "Данная программа поможет вам сконвертировать displace.bin вашей карты\n"
            "в .raw или .png формат.\n"
            "\n"
            "Для конвертирования файла вам необходимо выбрать файл displace.bin в папке карты, выбрать формат (raw или png) и выбрать размер карты (512 или 1024).\n"
            "\n"
            "После этого нажать кнопку 'Преобразовать файл'. В случае успеха вы увидите соответствующее сообщение\n"
            "и в папке появится файл в выбранном вами формате.\n"
            "\n"
            "Справка по размеру карт: 512 - по размеру как Край. 1024 - по размеру как Фатерлянд, Вахат\n"
            "\n"
            "Автор программы: стакан\n"
            "Автор скрипта конвертирования: ThePlain\n"
            "\n"
            "Создано для удобства мододелов сообщества Deus Ex Machina :)"
        ),
        "help_print": "Закрыто диалоговое окно помощи",
        "struct_error": (
            "Произошла ошибка при конвертации файла.\n"
            "\n"
            "Пожалуйста, проверьте выбранный размер карты (допустимые значения: 512 или 1024).\n"
            "\n"
            "Для получения дополнительной информации откройте раздел помощи."
        ),
        "wrong_extension": "Неверное расширение файла! Пожалуйста, выберите файл формата .bin!"
    },
    "uk": {
        "title": "displace.bin конвертер",
        "error": "Помилка",
        "sel_file": "Будь ласка, виберіть файл",
        "select_file": "Вибраний файл",
        "file_saved": "Файл збережено як",
        "conv_result": "Результат обробки",
        "result": "Результат",
        "plssel_file": "Будь ласка, виберіть файл, формат та розмір.",
        "sel_button": "Вибрати файл",
        "select_size": "Виберіть розмір",
        "convert_file": "Перетворити файл",
        "select_format": "Виберіть формат вихідного файлу:",
        "help": "Допомога",
        "help_text": (
            "Ця програма допоможе вам перетворити displace.bin вашої карти\n"
            "в .raw або .png формат.\n"
            "\n"
            "Щоб перетворити файл, вам потрібно вибрати файл displace.bin у папці з картою, вибрати формат (raw або png) та вибрати розмір карти (512 або 1024).\n"
            "\n"
            "Після цього натисніть кнопку 'Перетворити файл'. У разі успіху ви побачите повідомлення про успіх\n"
            "і файл у вибраному вами форматі з'явиться у папці.\n"
            "\n"
            "Довідка про розміри карт: 512 - за розміром як Край. 1024 - за розміром як Фатерлянд, Вахат\n"
            "\n"
            "Автор програми: стакан\n"
            "Автор скрипта перетворення: ThePlain\n"
            "\n"
            "Створено для зручності моддерів у спільноті Deus Ex Machina :)"
        ),
        "help_print": "Діалогове вікно допомоги закрито",
        "struct_error": (
            "Сталася помилка під час перетворення файлу.\n"
            "\n"
            "Будь ласка, перевірте обраний розмір карти (допустимі значення: 512 або 1024).\n"
            "\n"
            "Для отримання додаткової інформації відкрийте розділ допомоги."
        ),
        "wrong_extension": "Невірне розширення файлу! Будь ласка, виберіть файл формату .bin!"
    }
}



# Detect system language
system_lang = locale.getdefaultlocale()[0][:2]
lang = translations.get(system_lang, translations["en"])

# RAW convert
def process_raw(input_path, output_path, size):
    with open(input_path, 'rb') as stream:
        raw = struct.unpack(f'{size ** 2}f', stream.read())

    _min = min(raw)
    _max = max(raw)
    _del = _max - _min

    def mut(v):
        rel = v
        rel -= _min
        rel /= _del
        rel *= 0xFFFF
        rel = int(rel)
        return rel

    with open(output_path, 'wb') as stream:
        data = struct.pack(f'{size ** 2}H', *map(mut, raw))
        stream.write(data)

    return _min, _max, _del

# PNG convert
def process_png(input_path, output_path, size):
    with open(input_path, 'rb') as stream:
        raw = struct.unpack(f'{size ** 2}f', stream.read())

    _min = min(raw)
    _max = max(raw)
    _del = _max - _min

    def mut(v):
        rel = v
        rel -= _min
        rel /= _del
        rel *= 0xFFFF
        rel = int(rel)
        return rel

    normalized_data = list(map(mut, raw))

    image = Image.new('I', (size, size))
    image.putdata(normalized_data)
    image.save(output_path)

    return _min, _max, _del

# main function
def main(page: ft.Page):
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

    # Создание колонки с выравниванием по центру
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

    # file select
    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal input_file_path
        if e.files:
            input_file_path = e.files[0].path
        
        # Проверка на формат .bin
        if not input_file_path.lower().endswith('.bin'):
            show_error_dialog(lang["error"], lang["wrong_extension"])
            input_file_path = None  # Сбросить путь файла, если он некорректный
            return
            
        file_name.value = input_file_path  # Update the value in the input field
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

    # file picker init
    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)
    
    def select_file(e):
        file_picker.pick_files()

    # show result func
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
            dialog_open = False  # Close dialog state
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

    # process file func
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
                # Handle struct.error
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
            # The window requesting to select a file opens only if nothing is selected
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


    file_name = ft.TextField(
        value="",  # Initially empty value
        label=lang["select_file"],
        read_only=True,  # Disallow editing
        width=550  # You can set the desired width
    )

    select_button = ft.ElevatedButton(lang["sel_button"], on_click=select_file)

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
        on_hover=change_icon 
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
                        ft.Row([process_button], alignment=ft.MainAxisAlignment.CENTER)  # Центрируем кнопку
                    ],
                    spacing=10,
                ),
                padding=ft.padding.all(10),
            ),
            ft.Divider(color="transparent"),

                ft.Container(
                    help_btn_container,
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(10),
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
