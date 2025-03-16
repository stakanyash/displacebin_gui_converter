# displace.bin GUI Converter

![logo](https://github.com/user-attachments/assets/f63de348-033f-4404-b24f-072d999fb998)

This program helps you convert your map's `displace.bin` files into `.raw` or `.png` format. It is designed to simplify the conversion process.

## Table of Contents

- [Features](#features)
- [How to Use](#how-to-use)
- [Download](#download)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Program](#running-the-program-from-source-code)
- [License](#license)
- [Acknowledgments](#authors)

## Features

- **File Selection**: Select a `displace.bin` file from your map folder.
- **Format Selection**: Choose the output file format (`.raw` or `.png`).
- **Size Selection**: Choose the map size.
- **Conversion**: Convert the selected file to the desired format and size.
- **Help Section**: Provides detailed instructions and information about the program.
- **Multilanguage support**: This program supports the following languages: Russian, English, Ukrainian, Belarusian, and Polish.

**NOTE**: The Ukrainian and Polish localizations are in "not-verified" status and may contain translation errors. If you find an error in the translation, please create an issue or a merge request.

## How to Use

1. **File Selection**: Click the "Select File" button to choose a `displace.bin` file from your map folder.
2. **Format Selection**: Choose the output file format (`.raw` or `.png`).
3. **Size Selection**: Choose the map size.
4. **File Conversion**: Click the "Convert File" button to start the conversion process.
5. **View Result**: If the conversion is successful, you will see a success message, and the converted file will appear in the folder.

## Download

**Download the compiled file here:** https://github.com/stakanyash/displacebin_gui_converter/releases

## Requirements

- Python 3.x
- Flet
- PIL (Pillow)
- struct

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/stakanyash/displacebin_gui_converter.git
   ```

2. Navigate to the project directory:
   ```bash
   cd displacebin_gui_converter
   ```

3. Install the necessary dependencies:
   ```bash
   pip install requirements.txt
   ```

## Running the Program from Source Code

To run the program, execute the following command:
```bash
python src/main.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Authors

- **Program Author**: stakan
- **Conversion Script Author**: [ThePlain](https://github.com/ThePlain)
