import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../language_provider.dart';

void showSettingsDialog(BuildContext context, Function(String) onLanguageSelected) {
  var langProvider = Provider.of<LanguageProvider>(context, listen: false);
  showDialog(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: Text(langProvider.localizedStrings["sel_lang"] ?? "Select language"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextButton(onPressed: () => onLanguageSelected("ru"), child: Text("Русский")),
            TextButton(onPressed: () => onLanguageSelected("en"), child: Text("English")),
            TextButton(onPressed: () => onLanguageSelected("uk"), child: Text("Українська")),
            TextButton(onPressed: () => onLanguageSelected("be"), child: Text("Беларуская")),
            TextButton(onPressed: () => onLanguageSelected("pl"), child: Text("Polski")),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text("Отмена"),
          ),
        ],
      );
    },
  );
}
