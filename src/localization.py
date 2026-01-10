translations = {
    "En": {
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
            "8x8 - map with levelsize value '8'.\n"
            "16x16 - map with levelsize value '16'.\n"
            "32x32 - map with levelsize value '32'.\n"
            "64x64 - map with levelsize value '64'.\n"
            "\n"
            "You can find the levelsize value by opening the .ssl file of your map in text mode (for example via VS Code).\n"
        ),
        "struct_error": (
            "An error occurred while converting the file. Please check the selected map size.\n"
            "\n"
            "For more information, see the help section."
        ),
        "wrong_extension": "Wrong file extension! Please select a .bin file!",
        "sel_lang": "Select language",
        "cancel": "Cancel",
        "menu": "Menu",
        "cnglang": "Change language",
        "toggletheme": "Switch theme",
        "github": "GitHub repository",
        "discord": "Discord server",
        "telegram": "Telegram channel",
        "youtube": "YouTube channel",
        "zerodiv_error": (
            "Oops! An unexpected error occurred during the conversion process!\n"
            "\n"
            "Please contact the program developer and attach the log file."
        ),
        "opengit": "Open Github",
        "min": "Minimize",
        "exit": "Exit",
        "wrong_extension_reverse": "Selected file is not .raw!",
        "invalid_json_metadata": "JSON file is not selected or contains invalid data. Make sure you selected the correct file!",
        "meta_path": "Metadata file saved to:",
        "json": "JSON metadata file",
        "modeswitch1": "Switch to \".bin to .raw/.png\" converter",
        "modeswitch2": "Switch to \".raw/.png to .bin\" converter",
        "reversehelp_text": (
            "This mode of the \"DisplaceBox\" program helps you convert a raw or png format file back to bin format.\n"
            "\n"
            "To convert a file, you need to select a file with a .raw or .png extension and choose a JSON metadata file (see Help in the main mode for details).\n"
            "\n"
            "The size is calculated automatically.\n"
            "\n"
            "After selecting the files, press the \"Convert File\" button. If successful, you will see a confirmation message and the file \"displace.bin\" will appear in the folder. If it already exists, it will be overwritten.\n"
            "\n"
            "FAQ:\n"
            "Q: Can I use this to enlarge the map?\n"
            "A: No, you can’t. Increasing the map size is not limited to just increasing the heightmap size.\n"
            "\n"
            "Q: Can I perform reverse conversion without the metadata file?\n"
            "A: No, you can't. The metadata file contains critical information about the minimum and maximum terrain height.\n"
            "\n"
            "Q: What is this useful for?\n"
            "A: For cases where you want to manually edit the map terrain outside of M3D Editor.\n"
        ),
        "unsupportedfile": (
            "Oops! It looks like you're trying to convert a file that is not supported!\n"
            "\n"
            "Make sure the file is map data and that you have selected the correct metadata file.\n"
            "If you selected a PNG file as the main input, make sure it is 16-bit depth and in \"grayscale\" format."
        ),
        "wrong_extension_json": "The selected file is not a .json format file!",
        "metadatacheckbox": "Save metadata",
        "metadatainfo": "What are metadata for?",
        "meta_text": (
            "Metadata is required for \"reverse\" conversion.\n"
            "\n"
            "Metadata contains information about the minimum and maximum height of the landscape.\n"
            "Without this data, reverse conversion is IMPOSSIBLE!\n"
            "\n"
            "Metadata is saved in .json format inside the folder where the source .bin file is located."
        ),
        "info": "Info",
        "invalid_json_dgcver": "The 'DGCVer' field is missing or has an invalid format.",
        "invalid_json_version_format": "Version in the 'DGCVer' field is in an invalid format.",
        "json_from_older_version": (
            "The JSON file was generated in an older version of the program.\n"
            "The result may be inaccurate.\n"
            "\n"
            "Continue?"
        ),
        "json_from_newer_version": (
            "The JSON file was generated in a newer version of the program.\n"
            "Compatibility is not guaranteed.\n"
            "\n"
            "Continue?"
        ),
        "yes": "Yes",
        "no": "No",
        "warning": "Warning",
        "not_16bit_grayscale": "The selected PNG file is not a 16-bit grayscale image.",
        "invalid_png_file": "Unable to read the PNG file or it is corrupted.",
        "incomplete_16bit_data": "Input .raw file has incomplete 16-bit data. Make sure you selected the correct file!",
        "invalid_raw_file": "Unable to read the RAW file or it is corrupted.",
        "update_available": "Update available",
        "version_for_download": "Version available for download:",
        "update_now": "Update now",
        "update_downloaded": "Update downloaded",
        "restart": "The application will restart.",
        "downloading": "Downloading...",
        "update_error": "Update Error",
        "unexpected_error": "Unexpected error",
        "try_manual": "You can download the update manually from GitHub",
        "open_github": "Open GitHub",
        "file_size": "File size",
        "speed": "Speed",
    },

    # Russian language
    "Ru": {
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
            "8x8 - карта со значением levelsize '8'.\n"
            "16x16 - карта со значением levelsize '16'.\n"
            "32x32 - карта со значением levelsize '32'.\n"
            "64x64 - карта со значением levelsize '64'.\n"
            "\n"
            "Узнать значение levelsize можно открыв .ssl файл вашей карты в текстовом режиме (например через VS Code).\n"
        ),
        "struct_error": (
            "Произошла ошибка при конвертации файла. Пожалуйста, проверьте выбранный размер карты.\n"
            "\n"
            "Для получения дополнительной информации откройте раздел помощи."
        ),
        "wrong_extension": "Неверное расширение файла! Пожалуйста, выберите файл формата .bin!",
        "sel_lang": "Выберите язык",
        "cancel": "Отмена",
        "menu": "Меню",
        "cnglang": "Смена языка",
        "toggletheme": "Переключение темы",
        "github": "GitHub репозиторий",
        "discord": "Discord сервер",
        "telegram": "Telegram канал",
        "youtube": "YouTube канал",
        "zerodiv_error": (
            "Упс! В процессе конвертации произошла непредвиденная ошибка!\n" 
            "\n"
            "Обратитесь к разработчику программы, прикрепив лог-файл." 
        ),
        "opengit": "Открыть Github",
        "min": "Свернуть",
        "exit": "Закрыть",
        "wrong_extension_reverse": "Выбранный файл не является .raw или .png!",
        "invalid_json_metadata": "JSON-файл не выбран или содержит неверные данные. Убедитесь, что вы выбрали правильный файл!",
        "meta_path": "Путь к метаданным:",
        "json": "JSON-файл метаданных",
        "modeswitch1": "Переключиться на конвертер \".bin в .raw/.png\"",
        "modeswitch2": "Переключиться на конвертер \".raw/.png в .bin\"",
        "reversehelp_text": (
            "Данный режим программы \"DisplaceBox\" поможет вам сконвертировать файл формата raw или png обратно в bin формат.\n"
            "\n"
            "Для конвертирования файла вам необходимо выбрать файл с расширением raw или png и выбрать JSON файл метаданных (подробнее см. Помощь в режиме основной конвертации).\n"
            "\n"
            "Размер вычисляется автоматически.\n"
            "\n"
            "После выбора файлов нажать кнопку 'Преобразовать файл'. В случае успеха вы увидите соответствующее сообщение и в папке появится файл \"displace.bin\". В случае наличия файла он будет перезаписан.\n"
            "\n"
            "FAQ:\n"
            "В: Можно ли таким образом увеличить карту?\n"
            "О: Нет, нельзя. Увеличение размера карты не ограничивается только лишь увеличением размера карты высот.\n"
            "\n"
            "В: Можно ли произвести обратную конвертацию без файла метаданных?\n"
            "О: Нет, нельзя. Файл метаданных содержит критически необходимую информацию о минимальной и максимальной высоте ландшафта.\n"
            "\n"
            "В: Для чего это может быть полезно?\n"
            "О: Для случаев, если вы захотели вручную изменить ландшафт карты за пределами M3D Editor."
        ),
        "unsupportedfile": (
            "Упс! Кажется, вы пытаетесь сконвертировать файл, который не поддерживается!\n"
            "\n"
            "Убедитесь, что выбранный файл является данными карты и что вы выбрали правильный файл метаданных.\n"
            "Если в качестве основного файла вы выбрали PNG, убедитесь, что он имеет глубину 16 бит и формат \"grayscale\""
        ),
        "wrong_extension_json": "Выбранный файл не является файлом формата .json!",
        "metadatacheckbox": "Сохранять метаданные",
        "metadatainfo": "Для чего нужны метаданные?",
        "meta_text": (
            "Метаданные нужны для \"обратного\" конвертирования.\n"
            "\n"
            "Метаданные содержат в себе данные о минимальной и максимальной высоте ландшафта.\n"
            "При отсутствии этих данных обратное конвертирование НЕВОЗМОЖНО!\n"
            "\n"
            "Метаданные сохраняются в формате .json в папке в которой распологается исходный .bin файл."
        ),
        "info": "Инфо",
        "invalid_json_dgcver": "Поле 'DGCVer' отсутствует или имеет неверный формат.",
        "invalid_json_version_format": "Версия в поле 'DGCVer' указана в неверном формате.",
        "json_from_older_version": (
            "JSON файл был сгенерирован в более старой версии программы.\n"
            "Результат может быть неточным.\n"
            "\n"
            "Продолжить?"
        ),
        "json_from_newer_version": (
            "JSON файл был сгенерирован в более новой версии программы.\n"
            "Совместимость не гарантируется.\n"
            "\n"
            "Продолжить?"
        ),
        "yes": "Да",
        "no": "Нет",
        "warning": "Внимание",
        "not_16bit_grayscale": "Выбранный PNG-файл не является 16-битным изображением в градациях серого.",
        "invalid_png_file": "Невозможно прочитать файл PNG или он повреждён.",
        "incomplete_16bit_data": "Входной .raw файл содержит неполную 16-битную информацию. Убедитесь, что вы выбрали корректный файл!",
        "invalid_raw_file": "Невозможно прочитать файл RAW или он повреждён.",
        "update_available": "Доступно обновление",
        "version_for_download": "Для загрузки доступна версия:",
        "update_now": "Обновить",
        "update_downloaded": "Обновление загружено",
        "restart": "Приложение будет перезапущено.",
        "downloading": "Загрузка...",
        "update_error": "Ошибка обновления",
        "unexpected_error": "Неожиданная ошибка",
        "try_manual": "Вы можете скачать обновление вручную с GitHub",
        "open_github": "Открыть GitHub",
        "file_size": "Размер файла",
        "speed": "Скорость",
    },

    # Ukrainian language
    "Uk": {
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
            "8x8 - карта з значенням levelsize '8'.\n"
            "16x16 - карта з значенням levelsize '16'.\n"
            "32x32 - карта з значенням levelsize '32'.\n"
            "64x64 - карта з значенням levelsize '64'.\n"
            "\n"
            "Дізнатися значення levelsize можна відкривши .ssl файл вашої карти в текстовому режимі (наприклад через VS Code).\n"
        ),
        "struct_error": (
            "Сталася помилка під час конвертації файлу. Будь ласка, перевірте обраний розмір карти.\n"
            "\n"
            "Для отримання додаткової інформації відкрийте розділ допомоги."
        ),
        "wrong_extension": "Невірне розширення файлу! Будь ласка, виберіть файл формату .bin!",
        "sel_lang": "Виберіть мову",
        "cancel": "Скасування",
        "menu": "Меню",
        "cnglang": "Зміна мови",
        "toggletheme": "Переключення теми",
        "github": "GitHub репозиторій",
        "discord": "Discord сервер",
        "telegram": "Telegram канал",
        "youtube": "YouTube канал",
        "zerodiv_error": (
            "Упс! Під час конвертації сталася непередбачена помилка!\n"
            "\n"
            "Зверніться до розробника програми, додавши лог-файл."
        ),
        "opengit": "Відкрити Github",
        "min": "Згорнути",
        "exit": "Закрити",
        "wrong_extension_reverse": "Вибраний файл не є .raw або .png!",
        "invalid_json_metadata": "JSON-файл не вибрано або він містить некоректні дані. Переконайтесь, що ви вибрали правильний файл!",
        "meta_path": "Шлях до метаданих:",
        "json": "JSON-файл метаданих",
        "modeswitch1": "Перемкнутися на конвертер \".bin у .raw/.png\"",
        "modeswitch2": "Перемкнутися на конвертер \".raw/.png у .bin\"",
        "reversehelp_text": (
            "Цей режим програми \"DisplaceBox\" допоможе вам сконвертувати файл у форматі raw або png назад у формат bin.\n"
            "\n"
            "Щоб конвертувати файл, потрібно обрати файл з розширенням raw або png і обрати JSON-файл метаданих (детальніше див. Допомогу в основному режимі конвертації).\n"
            "\n"
            "Розмір обчислюється автоматично.\n"
            "\n"
            "Після вибору файлів натисніть кнопку 'Перетворити файл'. У разі успіху ви побачите відповідне повідомлення, і у папці з'явиться файл \"displace.bin\". Якщо файл вже існує, він буде перезаписаний.\n"
            "\n"
            "FAQ:\n"
            "П: Чи можна таким чином збільшити карту?\n"
            "В: Ні, не можна. Збільшення розміру карти не обмежується лише збільшенням розміру карти висот.\n"
            "\n"
            "П: Чи можна зробити зворотне перетворення без файлу метаданих?\n"
            "В: Ні, не можна. Файл метаданих містить критично важливу інформацію про мінімальну та максимальну висоту рельєфу.\n"
            "\n"
            "П: Для чого це може бути корисно?\n"
            "В: Для випадків, коли ви хочете вручну змінити рельєф карти поза межами M3D Editor.\n"
        ),
        "unsupportedfile": (
            "Ой! Схоже, ви намагаєтеся конвертувати файл, який не підтримується!\n"
            "\n"
            "Переконайтесь, що файл є даними карти і що ви вибрали правильний файл метаданих.\n"
            "Якщо основним файлом вибрано PNG, переконайтесь, що він має глибину 16 біт і формат \"grayscale\"."
        ),
        "wrong_extension_json": "Вибраний файл не є файлом у форматі .json!",
        "metadatacheckbox": "Зберігати метадані",
        "metadatainfo": "Для чого потрібні метадані?",
        "meta_text": (
            "Метадані необхідні для «зворотнього» перетворення.\n"
            "\n"
            "Метадані містять інформацію про мінімальну та максимальну висоту ландшафту.\n"
            "Без цих даних зворотне перетворення НЕМОЖЛИВЕ!\n"
            "\n"
            "Метадані зберігаються у форматі .json у папці, де розташований вихідний файл .bin."
        ),
        "info": "Інфо",
        "invalid_json_dgcver": "Поле 'DGCVer' відсутнє або має неправильний формат.",
        "invalid_json_version_format": "Версія у полі 'DGCVer' зазначена у неправильному форматі.",
        "json_from_older_version": (
            "JSON-файл створено у старшій версії програми.\n"
            "Результат може бути неточним.\n"
            "\n"
            "Продовжити?"
        ),
        "json_from_newer_version": (
            "JSON-файл створено у новішій версії програми.\n"
            "Сумісність не гарантовано.\n"
            "\n"
            "Продовжити?"
        ),
        "yes": "Так",
        "no": "Ні",
        "warning": "Увага",
        "not_16bit_grayscale": "Обраний PNG-файл не є 16-бітним зображенням у відтінках сірого.",
        "invalid_png_file": "Неможливо прочитати PNG-файл або він пошкоджений.",
        "incomplete_16bit_data": "Вхідний файл .raw містить неповні 16-бітні дані. Переконайтеся, що вибрали правильний файл!",
        "invalid_raw_file": "Неможливо прочитати RAW-файл або він пошкоджений.",
        "update_available": "Доступне оновлення",
        "version_for_download": "Для завантаження доступна версія:",
        "update_now": "Оновити",
        "update_downloaded": "Оновлення завантажено",
        "restart": "Програма буде перезапущена.",
        "downloading": "Завантаження...",
        "update_error": "Помилка оновлення",
        "unexpected_error": "Неочікувана помилка",
        "try_manual": "Ви можете завантажити оновлення вручну з GitHub",
        "open_github": "Відкрити GitHub",
        "file_size": "Розмір файлу",
        "speed": "Швидкість",
    },

    # Polish language
    "Pl": {
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
            "8x8 - mapa z wartością levelsize '8'.\n"
            "16x16 - mapa z wartością levelsize '16'.\n"
            "32x32 - mapa z wartością levelsize '32'.\n"
            "64x64 - mapa z wartością levelsize '64'.\n"
            "\n"
            "Wartość levelsize można znaleźć otwierając plik .ssl twojej mapy w trybie tekstowym (np. przez VS Code).\n"
        ),
        "struct_error": (
            "Wystąpił błąd podczas konwersji pliku. Proszę sprawdzić wybrany rozmiar mapy.\n"
            "\n"
            "Aby uzyskać więcej informacji, zobacz sekcję pomocy."
        ),
        "wrong_extension": "Nieprawidłowe rozszerzenie pliku! Proszę wybrać plik formatu .bin!",
        "sel_lang": "Wybierz język",
        "cancel": "Anuluj",
        "menu": "Menu",
        "cnglang": "Zmiana języka",
        "toggletheme": "Przełączanie motywu",
        "github": "Repozytorium GitHub",
        "discord": "Serwer Discord",
        "telegram": "Kanał Telegram",
        "youtube": "Kanał YouTube",
        "zerodiv_error": (
            "Ups! W trakcie konwersji wystąpił nieoczekiwany błąd.\n"
            "\n"
            "Proszę skontaktować się z programistą aplikacji i dołączyć plik dziennika (log)."
        ),
        "opengit": "Otwórz Github",
        "min": "Zminimalizuj",
        "exit": "Zamknij",
        "wrong_extension_reverse": "Wybrany plik nie jest formatu .raw lub .png!",
        "invalid_json_metadata": "Plik JSON nie został wybrany lub zawiera nieprawidłowe dane. Upewnij się, że wybrałeś poprawny plik!",
        "meta_path": "Ścieżka do metadanych:",
        "json": "Plik metadanych JSON",
        "modeswitch1": "Przełącz na konwerter \".bin do .raw/.png\"",
        "modeswitch2": "Przełącz na konwerter \".raw/.png do .bin\"",
        "reversehelp_text": (
            "Ten tryb programu \"DisplaceBox\" pomoże ci przekonwertować plik w formacie raw lub png z powrotem na format bin.\n"
            "\n"
            "Aby przekonwertować plik, należy wybrać plik z rozszerzeniem raw lub png oraz plik metadanych JSON (więcej informacji w Pomocy trybu głównego konwertowania).\n"
            "\n"
            "Rozmiar obliczany jest automatycznie.\n"
            "\n"
            "Po wybraniu plików kliknij przycisk 'Konwertuj plik'. W przypadku powodzenia zobaczysz odpowiedni komunikat, a w folderze pojawi się plik \"displace.bin\". Jeśli plik już istnieje, zostanie nadpisany.\n"
            "\n"
            "FAQ:\n"
            "P: Czy w ten sposób można powiększyć mapę?\n"
            "O: Nie, nie można. Zwiększenie rozmiaru mapy nie ogranicza się tylko do zwiększenia rozmiaru mapy wysokości.\n"
            "\n"
            "P: Czy można przeprowadzić konwersję wsteczną bez pliku metadanych?\n"
            "O: Nie, nie można. Plik metadanych zawiera krytyczne informacje o minimalnej i maksymalnej wysokości terenu.\n"
            "\n"
            "P: Do czego może się to przydać?\n"
            "O: W przypadkach, gdy chcesz ręcznie edytować teren mapy poza M3D Editor.\n"
        ),
        "unsupportedfile": (
            "Ups! Wygląda na to, że próbujesz przekonwertować plik, który nie jest obsługiwany!\n"
            "\n"
            "Upewnij się, że plik zawiera dane mapy i że wybrałeś poprawny plik metadanych.\n"
            "Jeśli jako plik główny wybrano PNG, upewnij się, że ma on głębię 16 bitów i format \"grayscale\"."
        ),
        "wrong_extension_json": "Wybrany plik nie jest plikiem w formacie .json!",
        "metadatacheckbox": "Zapisz metadane",
        "metadatainfo": "Do czego służą metadane?",
        "meta_text": (
            "Metadane są potrzebne do konwersji \"odwrotnej\".\n"
            "\n"
            "Metadane zawierają informacje o minimalnej i maksymalnej wysokości krajobrazu.\n"
            "Bez tych danych konwersja odwrotna jest NIEMOŻLIWA!\n"
            "\n"
            "Metadane zapisywane są w formacie .json w folderze, w którym znajduje się plik źródłowy .bin."
        ),
        "info": "Info",
        "invalid_json_dgcver": "Pole 'DGCVer' jest brakujące lub ma nieprawidłowy format.",
        "invalid_json_version_format": "Wersja w polu 'DGCVer' jest podana w nieprawidłowym formacie.",
        "json_from_older_version": (
            "Plik JSON został wygenerowany w starszej wersji programu.\n"
            "Wynik może być niedokładny.\n"
            "\n"
            "Kontynuować?"
        ),
        "json_from_newer_version": (
            "Plik JSON został wygenerowany w nowszej wersji programu.\n"
            "Kompatybilność nie jest zagwarantowana.\n"
            "\n"
            "Kontynuować?"
        ),
        "yes": "Tak",
        "no": "Nie",
        "warning": "Uwaga",
        "not_16bit_grayscale": "Wybrany plik PNG nie jest obrazem w skali szarości o głębi 16 bitów.",
        "invalid_png_file": "Nie można odczytać pliku PNG lub jest uszkodzony.",
        "incomplete_16bit_data": "Plik wejściowy .raw zawiera niekompletne dane 16-bitowe. Upewnij się, że wybrano poprawny plik!",
        "invalid_raw_file": "Nie można odczytać pliku RAW lub jest uszkodzony.",
        "update_available": "Dostępna aktualizacja",
        "version_for_download": "Dostępna wersja do pobrania:",
        "update_now": "Zaktualizuj teraz",
        "update_downloaded": "Aktualizacja pobrana",
        "restart": "Aplikacja zostanie ponownie uruchomiona.",
        "downloading": "Pobieranie...",
        "update_error": "Błąd aktualizacji",
        "unexpected_error": "Nieoczekiwany błąd",
        "try_manual": "Możesz pobrać aktualizację ręcznie z GitHub",
        "open_github": "Otwórz GitHub",
        "file_size": "Rozmiar pliku",
        "speed": "Prędkość",
    },

    # Belarusian language
    "Be": {
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
            "8x8 - карта з значэннем levelsize '8'.\n"
            "16x16 - карта з значэннем levelsize '16'.\n"
            "32x32 - карта з значэннем levelsize '32'.\n"
            "64x64 - карта з значэннем levelsize '64'.\n"
            "\n"
            "Даведацца значэнне levelsize можна адкрыўшы .ssl файл вашай карты ў тэкставым рэжыме (напрыклад праз VS Code).\n"
            "\n"
            "Праверка перакладу: nEmPoBu4, MrKirov\n"
        ),
        "struct_error": (
            "Адбылася памылка пры канвертаванні файла. Калі ласка, праверце выбраны памер карты.\n"
            "\n"
            "Каб атрымаць дадатковую інфармацыю, адкрыйце раздзел дапамогі."
        ),
        "wrong_extension": "Няправільнае пашырэнне файла! Калі ласка, выберыце файл фармату .bin!",
        "sel_lang": "Выберыце мову",
        "cancel": "Адмена",
        "menu": "Меню",
        "cnglang": "Змена мовы",
        "toggletheme": "Пераключэнне тэмы",
        "github": "GitHub рэпазіторый",
        "discord": "Discord сервер",
        "telegram": "Telegram канал",
        "youtube": "YouTube канал",
        "zerodiv_error": (
            "Упс! Падчас канвертацыі адбылася няспадзяваная памылка!\n"
            "\n"
            "Калі ласка, звярніцеся да распрацоўшчыка праграмы і далучыце лаг-файл."
        ),
        "opengit": "Адкрыць Github",
        "min": "Згарнуць",
        "exit": "Закрыць",
        "wrong_extension_reverse": "Выбраны файл не з'яўляецца .raw або .png!",
        "invalid_json_metadata": "JSON-файл не выбраны або змяшчае няправільныя дадзеныя. Пераканайцеся, што вы выбралі правільны файл!",
        "meta_path": "Шлях да метаданых:",
        "json": "JSON-файл метаданых",
        "modeswitch1": "Пераключыцца на канвертар \".bin у .raw/.png\"",
        "modeswitch2": "Пераключыцца на канвертар \".raw/.png у .bin\"",
        "reversehelp_text": (
            "Гэты рэжым праграмы \"DisplaceBox\" дапаможа вам сканвертаваць файл фармату raw або png назад у фармат bin.\n"
            "\n"
            "Каб сканвертаваць файл, неабходна выбраць файл з пашырэннем raw або png і выбраць JSON-файл метаданых (падрабязней гл. Дапамога ў асноўным рэжыме канвертацыі).\n"
            "\n"
            "Памер вызначаецца аўтаматычна.\n"
            "\n"
            "Пасля выбару файлаў націсніце кнопку 'Канвертаваць файл'. У выпадку поспеху вы ўбачыце адпаведнае паведамленне, і ў тэчцы з’явіцца файл \"displace.bin\". Калі файл ужо існуе, ён будзе перазапісаны.\n"
            "\n"
            "FAQ:\n"
            "П: Ці можна такім чынам павялічыць карту?\n"
            "А: Не, нельга. Павелічэнне памеру карты не абмяжоўваецца толькі павелічэннем памеру карты вышынь.\n"
            "\n"
            "П: Ці можна выканаць зваротную канвертацыю без файла метаданых?\n"
            "А: Не, нельга. Файл метаданых утрымлівае крытычна важную інфармацыю аб мінімальнай і максімальнай вышыні ландшафту.\n"
            "\n"
            "П: Навошта гэта можа быць карысна?\n"
            "А: Для выпадкаў, калі вы хочаце ўручную змяніць ландшафт карты па-за межамі M3D Editor.\n"
        ),
        "unsupportedfile": (
            "Упс! Падаецца, што вы спрабуеце сканвертаваць файл, які не падтрымліваецца!\n"
            "\n"
            "Пераканайцеся, што файл з'яўляецца данымі карты і што вы выбралі правільны файл метаданых.\n"
            "Калі вы выбралі PNG у якасці асноўнага файла, пераканайцеся, што ён мае глыбіню 16 бітаў і фармат \"grayscale\"."
        ),
        "wrong_extension_json": "Абраны файл не з'яўляецца файлам фармату .json!",
        "metadatacheckbox": "Захаваць метаданыя",
        "metadatainfo": "Для чаго патрэбныя метаданыя?",
        "meta_text": (
            "Метаданыя патрэбныя для \"зваротнага\" пераўтварэння.\n"
            "\n"
            "Метаданыя ўтрымліваюць інфармацыю пра мінімальную і максімальную вышыню ландшафту.\n"
            "Без гэтых даных зваротнае пераўтварэнне НЯМОЖНАЕ!\n"
            "\n"
            "Метаданыя захоўваюцца ў фармаце .json у тэчцы, дзе размяшчаецца зыходны файл .bin."
        ),
        "info": "Інфа",
        "invalid_json_dgcver": "Поле 'DGCVer' адсутнічае ці мае няправільны фармат.",
        "invalid_json_version_format": "Версія ў полі 'DGCVer' паказана ў няправільным фармаце.",
        "json_from_older_version": (
            "JSON-файл створаны ў старажытней версіі праграмы.\n" 
            "Вынік можа быць недакладным.\n"
            "\n"
            "Працягнуць?"
        ),
        "json_from_newer_version": (
            "JSON-файл створаны ў маладзей версіі праграмы.\n"
            "Сумяшчальнасць не гарантаваная.\n"
            "\n"
            "Працягнуць?"
        ),
        "yes": "Так",
        "no": "Не",
        "warning": "Увага",
        "not_16bit_grayscale": "Абраны PNG-файл не з'яўляецца 16-бітным выявай у адценні шэрага.",
        "invalid_png_file": "Немагчыма чытаць PNG-файл ці ён пашкоджаны.",
        "incomplete_16bit_data": "Уваходны файл .raw мае нецалыя 16-бітныя дадзеныя. Калі ласка, пераканайцеся, што вы пазначылі правільны файл!",
        "invalid_raw_file": "Немагчыма чытаць RAW-файл ці ён пашкоджаны.",
        "update_available": "Даступна абнаўленне",
        "version_for_download": "Для спампоўкі даступная версія:",
        "update_now": "Абнавіць",
        "update_downloaded": "Абнаўленне спампавана",
        "restart": "Праграма будзе перазапушчана.",
        "downloading": "Спампоўка...",
        "update_error": "Памылка абнаўлення",
        "unexpected_error": "Нечаканая памылка",
        "try_manual": "Вы можаце спампаваць абнаўленне ўручную з GitHub",
        "open_github": "Адкрыць GitHub",
        "file_size": "Памер файла",
        "speed": "Хуткасць",
    }
}