import 'dart:io';
import 'package:url_launcher/url_launcher.dart';

class Utils {
  static Future<void> openUrl(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(
        uri,
        mode: Platform.isWindows ? LaunchMode.platformDefault : LaunchMode.externalApplication,
      );
    } else {
      throw "Не удалось открыть $url";
    }
  }
}
