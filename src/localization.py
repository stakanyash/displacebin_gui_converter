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
        "select_size": "Select size (more on 'Help' page)",
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
        "wrong_extension": "Wrong file extension! Please select a .bin file!",
        "sel_lang": "Select language"
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
        "select_size": "Выберите размер (подробнее во вкладке 'Помощь')",
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
        "wrong_extension": "Неверное расширение файла! Пожалуйста, выберите файл формата .bin!",
        "sel_lang": "Выберите язык"
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
        "select_size": "Виберіть розмір (докладніше у вкладці 'Допомога')",
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
        "wrong_extension": "Невірне розширення файлу! Будь ласка, виберіть файл формату .bin!",
        "sel_lang": "Виберіть мову"
    }
}

system_lang = locale.getdefaultlocale()[0][:2]
lang = translations.get(system_lang, translations["en"])