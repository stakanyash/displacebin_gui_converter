import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/file_picker_widget.dart';
import '../theme_provider.dart';
import '../utils.dart';
import '../widgets/settings_dialog.dart';
import '../widgets/result_dialog.dart';
import '../file_processor.dart';
import '../language_provider.dart';
import 'widgets/animated_icon_button.dart';

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with SingleTickerProviderStateMixin {
  String? selectedFile;
  int? selectedSize;
  String? selectedFormat;
  bool _showBanner = false;
  String _bannerMessage = "";
  AnimationController? _animationController;
  Animation<Offset>? _offsetAnimation;
  Animation<double>? _opacityAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: Duration(milliseconds: 300),
      vsync: this,
    );
    _offsetAnimation = Tween<Offset>(
      begin: Offset(0, 1),
      end: Offset(0, 0),
    ).animate(CurvedAnimation(
      parent: _animationController!,
      curve: Curves.easeInOut,
    ));
    _opacityAnimation = Tween<double>(
      begin: 0,
      end: 1,
    ).animate(CurvedAnimation(
      parent: _animationController!,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController?.dispose();
    super.dispose();
  }

  void _processFile() async {
    var langProvider = Provider.of<LanguageProvider>(context, listen: false);

    if (selectedFile == null || selectedSize == null) {
      _showErrorBanner(langProvider.localizedStrings["plssel_file"] ?? "Please select a file, format, and size.");
      return;
    }

    try {
      String outputPath;
      if (selectedFormat == "raw") {
        outputPath = await FileProcessor.processBinToRaw(selectedFile!, selectedSize!, langProvider);
      } else {
        outputPath = await FileProcessor.processBinToPng(selectedFile!, selectedSize!, langProvider);
      }

      showResultDialog(context, outputPath);
    } catch (e) {
      _showErrorBanner("${langProvider.localizedStrings["error"]}: $e");
    }
  }

  void _showErrorBanner(String message) {
    setState(() {
      _bannerMessage = message;
      _showBanner = true;
      _animationController?.forward();
    });
  }

  void _hideBanner() {
    _animationController?.reverse().then((_) {
      setState(() {
        _showBanner = false;
      });
    });
  }

  Widget _buildSocialIcon(String assetPath, String url, {double size = 40}) {
    final themeProvider = Provider.of<ThemeProvider>(context, listen: false);
    final iconColor = themeProvider.themeMode == ThemeMode.dark
        ? Color(0xFF9ECAFF)
        : Colors.black;

    return IconButton(
      icon: ColorFiltered(
        colorFilter: ColorFilter.mode(iconColor, BlendMode.srcIn),
        child: Image.asset(assetPath, height: size, width: size),
      ),
      onPressed: () => Utils.openUrl(url),
    );
  }

  @override
  Widget build(BuildContext context) {
    var themeProvider = Provider.of<ThemeProvider>(context);
    var langProvider = Provider.of<LanguageProvider>(context);

    Color iconColor = themeProvider.themeMode == ThemeMode.dark
        ? Color(0xFF9ECAFF)
        : Colors.black;

    return Scaffold(
      body: Stack(
        children: [
          Padding(
            padding: EdgeInsets.all(4.0),
            child: Column(
              children: [
                SizedBox(height: 50),
                Image.asset(
                  themeProvider.themeMode == ThemeMode.dark
                      ? "lib/src_assets/logo.png"
                      : "lib/src_assets/logo_white.png",
                  height: 100,
                ),
                Expanded(
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        FilePickerWidget(
                          onFileSelected: (file) {
                            setState(() {
                              selectedFile = file;
                            });
                          },
                        ),
                        SizedBox(height: 40),
                        Text(langProvider.localizedStrings["select_format"] ?? "Select the format of the output file:"),
                        SizedBox(height: 10),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Radio(
                              value: "raw",
                              groupValue: selectedFormat,
                              onChanged: (value) {
                                setState(() {
                                  selectedFormat = value.toString();
                                });
                              },
                            ),
                            Text(".raw"),
                            SizedBox(width: 20),
                            Radio(
                              value: "png",
                              groupValue: selectedFormat,
                              onChanged: (value) {
                                setState(() {
                                  selectedFormat = value.toString();
                                });
                              },
                            ),
                            Text(".png"),
                          ],
                        ),
                        SizedBox(height: 40),
                        SizedBox(
                          width: MediaQuery.of(context).size.width * 0.8,
                          child: DropdownButtonFormField<int>(
                            value: selectedSize,
                            decoration: InputDecoration(
                              hintText: langProvider.localizedStrings["select_size"] ?? "Select size",
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12),
                            ),
                            items: [
                              DropdownMenuItem(value: 128, child: Text("8x8")),
                              DropdownMenuItem(value: 256, child: Text("16x16")),
                              DropdownMenuItem(value: 512, child: Text("32x32")),
                              DropdownMenuItem(value: 1024, child: Text("64x64")),
                            ],
                            onChanged: (int? newValue) {
                              setState(() {
                                selectedSize = newValue;
                              });
                            },
                          ),
                        ),
                        SizedBox(height: 40),
                        ElevatedButton(
                          onPressed: _processFile,
                          child: Text(langProvider.localizedStrings["convert_file"] ?? "Convert file"),
                        ),
                      ],
                    ),
                  ),
                ),
                Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Tooltip(
                          message: langProvider.localizedStrings["help"] ?? "Help",
                          child: AnimatedIconButton(
                            defaultIcon: Icons.help_outline,
                            hoverIcon: Icons.help,
                            onPressed: () => showHelpDialog(context),
                            color: iconColor,
                          ),
                        ),
                        SizedBox(width: 20),
                        Tooltip(
                          message: langProvider.localizedStrings["sel_lang"] ?? "Select language",
                          child: AnimatedIconButton(
                            defaultIcon: Icons.language,
                            hoverIcon: Icons.lens_rounded,
                            onPressed: () {
                              showSettingsDialog(context, (lang) {
                                langProvider.setLanguage(lang);
                                setState(() {});
                              });
                            },
                            color: iconColor,
                          ),
                        ),
                        SizedBox(width: 20),
                        Tooltip(
                          message: themeProvider.themeMode == ThemeMode.dark
                              ? langProvider.localizedStrings["light_mode"] ?? "Switch to white theme"
                              : langProvider.localizedStrings["dark_mode"] ?? "Switch to dark theme",
                          child: AnimatedIconButton(
                            defaultIcon: themeProvider.themeMode == ThemeMode.dark
                                ? Icons.nightlight_round
                                : Icons.wb_sunny,
                            hoverIcon: themeProvider.themeMode == ThemeMode.dark
                                ? Icons.wb_sunny
                                : Icons.nightlight_round,
                            onPressed: themeProvider.toggleTheme,
                            color: iconColor,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 5),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Tooltip(
                          message: langProvider.localizedStrings["github"] ?? "GitHub repository",
                          child: _buildSocialIcon("lib/src_assets/git.png", "https://github.com/stakanyash/displacebin_gui_converter/tree/dart_alpha", size: 25),
                        ),
                        SizedBox(width: 20),
                        Tooltip(
                          message: langProvider.localizedStrings["discord"] ?? "Discord server",
                          child: _buildSocialIcon("lib/src_assets/dis.png", "https://discord.com/invite/Cd5GanuYud", size: 25),
                        ),
                        SizedBox(width: 20),
                        Tooltip(
                          message: langProvider.localizedStrings["telegram"] ?? "Telegram channel",
                          child: _buildSocialIcon("lib/src_assets/tg.png", "https://t.me/stakanyasher", size: 25),
                        ),
                        SizedBox(width: 20),
                        Tooltip(
                          message: langProvider.localizedStrings["youtube"] ?? "YouTube channel",
                          child: _buildSocialIcon("lib/src_assets/yt.png", "https://www.youtube.com/@stakanyash", size: 25),
                        ),
                      ],
                    ),
                    SizedBox(height: 20),
                    Align(
                      alignment: Alignment.bottomRight,
                      child: Padding(
                        padding: EdgeInsets.only(right: 10, bottom: 10),
                        child: Text(
                          "Dart 0.8.1 [250320]",
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.grey,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (_showBanner)
            Positioned(
              bottom: 20,
              left: 20,
              right: 20,
              child: SlideTransition(
                position: _offsetAnimation!,
                child: FadeTransition(
                  opacity: _opacityAnimation!,
                  child: Material(
                    elevation: 5.0,
                    color: Colors.red.shade700,
                    child: Padding(
                      padding: EdgeInsets.all(16.0),
                      child: Row(
                        children: [
                          Icon(
                            Icons.error_outline,
                            color: Colors.white,
                            size: 24,
                          ),
                          SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _bannerMessage,
                                  style: TextStyle(color: Colors.white),
                                ),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.end,
                                  children: [
                                    TextButton(
                                      onPressed: _hideBanner,
                                      child: Text("OK", style: TextStyle(color: Colors.white)),
                                    ),
                                    TextButton(
                                      onPressed: () {
                                        _hideBanner();
                                        showHelpDialog(context);
                                      },
                                      child: Text(langProvider.localizedStrings["help"] ?? "Help", style: TextStyle(color: Colors.white)),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  void showHelpDialog(BuildContext context) {
    var langProvider = Provider.of<LanguageProvider>(context, listen: false);

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(langProvider.localizedStrings["help"] ?? "Помощь"),
          content: Text(
            langProvider.localizedStrings["help_text"] ??
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
            "\n"
            "Program author: stakan\n"
            "Conversion script author: ThePlain\n"
            "\n"
            "Porting to Dart was done with the help of ChatGPT.",
            textAlign: TextAlign.left,
          ),
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
}
