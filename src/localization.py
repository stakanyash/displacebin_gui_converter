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
        "select_size": "Select size (see 'Help' tab for more details)",
        "convert_file": "Convert file",
        "select_format": "Select the format of the output file:",
        "help": "Help",
        "help_text": (
            "This program will help you convert the displace.bin of your map\n"
            "to .raw or .png format.\n"
            "\n"
            "To convert the file, you need to select the displace.bin file in the map folder, choose the format (raw or png), and select the map size.\n"
            "\n"
            "After that, click the 'Convert file' button. If successful, you will see a corresponding message\n"
            "and a file in the selected format will appear in the folder.\n"
            "\n"
            "Map size reference:\n"
            "16x16 - map with levelsize value '16'.\n"
            "32x32 - map with levelsize value '32'.\n"
            "64x64 - map with levelsize value '64'.\n"
            "128x128 - map with levelsize value '128'.\n"
            "\n"
            "You can find the levelsize value by opening the .ssl file of your map in text mode (for example via VS Code).\n"
            "\n"
            "Program author: stakan\n"
            "Conversion script author: ThePlain\n"
        ),
        "help_print": "Help dialog closed",
        "struct_error": (
            "An error occurred while converting the file. Please check the selected map size.\n"
            "\n"
            "For more information, see the help section."
        ),
        "wrong_extension": "Wrong file extension! Please select a .bin file!",
        "sel_lang": "Select language",
        "cancel": "Cancel",
        "menu": "Menu"
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
            "Для конвертирования файла вам необходимо выбрать файл displace.bin в папке карты, выбрать формат (raw или png) и выбрать размер карты.\n"
            "\n"
            "После этого нажать кнопку 'Преобразовать файл'. В случае успеха вы увидите соответствующее сообщение\n"
            "и в папке появится файл в выбранном вами формате.\n"
            "\n"
            "Справка по размеру карт:\n"
            "16x16 - карта со значением levelsize '16'.\n"
            "32x32 - карта со значением levelsize '32'.\n"
            "64x64 - карта со значением levelsize '64'.\n"
            "128x128 - карта со значением levelsize '128'.\n"
            "\n"
            "Узнать значение levelsize можно открыв .ssl файл вашей карты в текстовом режиме (например через VS Code).\n"
            "\n"
            "Автор программы: стакан\n"
            "Автор скрипта конвертирования: ThePlain\n"
        ),
        "help_print": "Закрыто диалоговое окно помощи",
        "struct_error": (
            "Произошла ошибка при конвертации файла. Пожалуйста, проверьте выбранный размер карты.\n"
            "\n"
            "Для получения дополнительной информации откройте раздел помощи."
        ),
        "wrong_extension": "Неверное расширение файла! Пожалуйста, выберите файл формата .bin!",
        "sel_lang": "Выберите язык",
        "cancel": "Отмена",
        "menu": "Меню"
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
            "Щоб перетворити файл, вам потрібно вибрати файл displace.bin у папці з картою, вибрати формат (raw або png) та вибрати розмір карти.\n"
            "\n"
            "Після цього натисніть кнопку 'Перетворити файл'. У разі успіху ви побачите повідомлення про успіх\n"
            "і файл у вибраному вами форматі з'явиться у папці.\n"
            "\n"
            "Довідка по розміру карт:\n"
            "16x16 - карта з значенням levelsize '16'.\n"
            "32x32 - карта з значенням levelsize '32'.\n"
            "64x64 - карта з значенням levelsize '64'.\n"
            "128x128 - карта з значенням levelsize '128'.\n"
            "\n"
            "Дізнатися значення levelsize можна відкривши .ssl файл вашої карти в текстовому режимі (наприклад через VS Code).\n"
            "\n"
            "Автор програми: стакан\n"
            "Автор скрипта перетворення: ThePlain\n"
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
        "sel_lang": "Виберіть мову",
        "cancel": "Скасування",
        "menu": "Меню"
    },
    "pl": {
        "title": "Konwerter displace.bin",
        "error": "Błąd",
        "sel_file": "Proszę wybrać plik",
        "select_file": "Wybrany plik",
        "file_saved": "Plik zapisany jako",
        "conv_result": "Wynik przetwarzania",
        "result": "Wynik",
        "plssel_file": "Proszę wybrać plik, format i rozmiar.",
        "sel_button": "Wybierz plik",
        "select_size": "Wybierz rozmiar (więcej informacji w zakładce 'Pomoc')",
        "convert_file": "Konwertuj plik",
        "select_format": "Wybierz format pliku wyjściowego:",
        "help": "Pomoc",
        "help_text": (
            "Ten program pomoże Ci skonwertować displace.bin Twojej mapy\n"
            "do formatu .raw lub .png.\n"
            "\n"
            "Aby skonwertować plik, musisz wybrać plik displace.bin w folderze mapy, wybrać format (raw lub png) i wybrać rozmiar mapy.\n"
            "\n"
            "Następnie naciśnij przycisk 'Konwertuj plik'. W przypadku sukcesu zobaczysz odpowiedni komunikat\n"
            "i plik w wybranym formacie pojawi się w folderze.\n"
            "\n"
            "Informacje o rozmiarze map:\n"
            "16x16 - mapa z wartością levelsize '16'.\n"
            "32x32 - mapa z wartością levelsize '32'.\n"
            "64x64 - mapa z wartością levelsize '64'.\n"
            "128x128 - mapa z wartością levelsize '128'.\n"
            "\n"
            "Wartość levelsize można znaleźć otwierając plik .ssl Twojej mapy w trybie tekstowym (np. przez VS Code).\n"
            "\n"
            "Autor programu: stakan\n"
            "Autor skryptu konwersji: ThePlain\n"
        ),
        "help_print": "Zamknięto okno dialogowe pomocy",
        "struct_error": (
            "Wystąpił błąd podczas konwersji pliku. Proszę sprawdzić wybrany rozmiar mapy.\n"
            "\n"
            "Aby uzyskać więcej informacji, zobacz sekcję pomocy."
        ),
        "wrong_extension": "Nieprawidłowe rozszerzenie pliku! Proszę wybrać plik formatu .bin!",
        "sel_lang": "Wybierz język",
        "cancel": "Anuluj",
        "menu": "Menu"
    },
    "be": {
        "title": "displace.bin канвертар",
        "error": "Памылка",
        "sel_file": "Калі ласка, выберыце файл",
        "select_file": "Выбраны файл",
        "file_saved": "Файл захаваны як",
        "conv_result": "Вынік апрацоўкі",
        "result": "Вынік",
        "plssel_file": "Калі ласка, выберыце файл, фармат і памер.",
        "sel_button": "Выбраць файл",
        "select_size": "Выберыце памер (падрабязней у раздзеле 'Дапамога')",
        "convert_file": "Канвертаваць файл",
        "select_format": "Выберыце фармат выхаднога файла:",
        "help": "Дапамога",
        "help_text": (
            "Гэтая праграма дапаможа вам канвертаваць displace.bin вашай карты\n"
            "у фармат .raw або .png.\n"
            "\n"
            "Каб канвертаваць файл, вам трэба выбраць файл displace.bin у тэчцы з картай, выбраць фармат (raw або png) і выбраць памер карты.\n"
            "\n"
            "Пасля гэтага націсніце кнопку 'Канвертаваць файл'. У выпадку поспеху вы ўбачыце адпаведны паведамленне\n"
            "і файл у выбраным вамі фармаце з'явіцца ў тэчцы.\n"
            "\n"
            "Даведка па памеру карт:\n"
            "16x16 - карта з значэннем levelsize '16'.\n"
            "32x32 - карта з значэннем levelsize '32'.\n"
            "64x64 - карта з значэннем levelsize '64'.\n"
            "128x128 - карта з значэннем levelsize '128'.\n"
            "\n"
            "Даведацца значэнне levelsize можна адкрыўшы .ssl файл вашай карты ў тэкставым рэжыме (напрыклад праз VS Code).\n"
            "\n"
            "Аўтар праграмы: стакан\n"
            "Аўтар скрыпта канвертавання: ThePlain\n"
        ),
        "help_print": "Закрытае дыялогавае акно дапамогі",
        "struct_error": (
            "Адбылася памылка пры канвертаванні файла. Калі ласка, праверце выбраны памер карты.\n"
            "\n"
            "Каб атрымаць дадатковую інфармацыю, адкрыйце раздзел дапамогі."
        ),
        "wrong_extension": "Няправільнае пашырэнне файла! Калі ласка, выберыце файл фармату .bin!",
        "sel_lang": "Выберыце мову",
        "cancel": "Адмена",
        "menu": "Меню"
    }
}

system_lang = locale.getdefaultlocale()[0][:2]
lang = translations.get(system_lang, translations["en"])