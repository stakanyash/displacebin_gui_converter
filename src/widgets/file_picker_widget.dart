import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../language_provider.dart';
import 'package:provider/provider.dart';

class FilePickerWidget extends StatefulWidget {
  final Function(String) onFileSelected;

  const FilePickerWidget({required this.onFileSelected, Key? key}) : super(key: key);

  @override
  _FilePickerWidgetState createState() => _FilePickerWidgetState();
}

class _FilePickerWidgetState extends State<FilePickerWidget> {
  String? _filePath;

  void _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['bin'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _filePath = result.files.single.path!;
      });
      widget.onFileSelected(_filePath!);
    }
  }

  @override
  Widget build(BuildContext context) {
    var langProvider = Provider.of<LanguageProvider>(context, listen: false);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center, // Центрирование элементов
      children: [
        // Поле ввода с путём к файлу
        SizedBox(
          width: 580, // Ограничиваем ширину поля ввода
          child: TextField(
            controller: TextEditingController(text: _filePath ?? ""),
            readOnly: true,
            decoration: InputDecoration(
              labelText: langProvider.localizedStrings["select_file"] ?? "Selected file",
              border: OutlineInputBorder(),
            ),
          ),
        ),
        SizedBox(height: 10), // Отступ между полем и кнопкой

        // Кнопка "Выбрать файл" с ограниченной шириной
        SizedBox(
          width: 150, // Ограничиваем ширину кнопки
          child: ElevatedButton(
            onPressed: _pickFile,
            child: Text(langProvider.localizedStrings["sel_button"] ?? "Select file"),
          ),
        ),
      ],
    );
  }
}
