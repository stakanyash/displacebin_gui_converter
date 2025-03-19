import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:window_manager/window_manager.dart';
import 'home_page.dart';
import 'theme_provider.dart';
import 'language_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();

  WindowOptions windowOptions = WindowOptions(
    size: Size(640, 800),
    minimumSize: Size(640, 800),
    center: true,
    fullScreen: false,
    backgroundColor: Colors.transparent,
  );

  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.setPreventClose(false);
    await windowManager.setAlwaysOnTop(false);
    await windowManager.setResizable(false);
    await windowManager.setMaximizable(false);

    LanguageProvider langProvider = LanguageProvider();
    await langProvider.loadSavedLanguage();
    await windowManager.setTitle(langProvider.localizedStrings["title"] ?? "displace.bin Converter");
  });

  LanguageProvider languageProvider = LanguageProvider();
  await languageProvider.loadSavedLanguage();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => ThemeProvider()),
        ChangeNotifierProvider(create: (context) => languageProvider),
      ],
      child: MyApp(),
    ),
  );
}


class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    var themeProvider = Provider.of<ThemeProvider>(context);
    var langProvider = Provider.of<LanguageProvider>(context);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: langProvider.localizedStrings["title"] ?? "displace.bin Converter",
      themeMode: themeProvider.themeMode,
      theme: ThemeData.light(),
      darkTheme: ThemeData.dark(),
      home: HomePage(),
    );
  }
}
