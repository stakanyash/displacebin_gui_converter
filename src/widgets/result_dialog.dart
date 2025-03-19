import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../language_provider.dart';

void showResultDialog(BuildContext context, String outputPath) {
  var langProvider = Provider.of<LanguageProvider>(context, listen: false);
  showDialog(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: Text(langProvider.localizedStrings["result"] ?? "Result"),
        content: Text("${langProvider.localizedStrings["file_saved"] ?? "File saved as"}:\n$outputPath"),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text("OK"),
          ),
        ],
      );
    },
  );
}
