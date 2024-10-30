# displace.bin GUI конвертер

![icon1](https://github.com/user-attachments/assets/5d407247-d70d-45ce-923d-26cb401d9be4)

Эта программа помогает вам конвертировать файлы `displace.bin` вашей карты в формат `.raw` или `.png`. Она разработана для упрощения процесса конвертации.

## Оглавление

- [Возможности](#возможности)
- [Как использовать](#как-использовать)
- [Требования](#требования)
- [Установка](#установка)
- [Запуск программы](#запуск-программы-из-исходного-кода)
- [Лицензия](#лицензия)
- [Благодарности](#благодарности)

## Возможности

- **Выбор файла**: Выберите файл `displace.bin` из папки с картой.
- **Выбор формата**: Выберите формат выходного файла (`.raw` или `.png`).
- **Выбор размера**: Выберите размер карты (512 или 1024).
- **Конвертация**: Преобразуйте выбранный файл в нужный формат и размер.
- **Раздел помощи**: Предлагает подробные инструкции и информацию о программе.

## Как использовать

1. **Выбор файла**: Нажмите кнопку "Выбрать файл", чтобы выбрать файл `displace.bin` из папки с картой.
2. **Выбор формата**: Выберите формат выходного файла (`.raw` или `.png`).
3. **Выбор размера**: Выберите размер карты (512 или 1024).
4. **Конвертация файла**: Нажмите кнопку "Преобразовать файл", чтобы начать процесс конвертации.
5. **Просмотр результата**: В случае успешной конвертации вы увидите сообщение об успехе, и преобразованный файл появится в папке.

## Требования

- Python 3.x
- Flet
- PIL (Pillow)
- struct

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/displace-bin-converter.git
   ```

2. Перейдите в директорию проекта:
   ```bash
   cd displace-bin-converter
   ```

3. Установите необходимые зависимости:
   ```bash
   pip install requirements.txt
   ```

## Запуск программы из исходного кода

Для запуска программы выполните следующую команду:
```bash
python main.py
```

## Лицензия

Этот проект лицензирован под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## Авторы

- **Автор программы**: stakan
- **Автор скрипта конвертации**: [ThePlain](https://github.com/ThePlain)
