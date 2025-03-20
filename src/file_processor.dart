import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'package:image/image.dart';
import '../language_provider.dart';
import 'package:provider/provider.dart';

class FileProcessor {
  /// Converts `.bin` to `.raw`
  static Future<String> processBinToRaw(String filePath, int size, LanguageProvider langProvider) async {
    final inputFile = File(filePath);
    if (!await inputFile.exists()) {
      throw langProvider.localizedStrings["file_not_found"] ?? "File not found!";
    }

    final outputFilePath = filePath.replaceAll('.bin', '.raw');
    final outputFile = File(outputFilePath);

    // Read binary data
    Uint8List bytes = await inputFile.readAsBytes();

    // Check data size
    if (bytes.length != size * size * 4) {
      throw langProvider.localizedStrings["struct_error"] ?? "An error occurred while converting the file. Please check the selected map size.\n\nFor more information, see the help section.";
    }

    ByteData byteData = ByteData.sublistView(bytes);
    List<double> rawData = List.generate(size * size, (i) => byteData.getFloat32(i * 4, Endian.little));

    // Normalize data
    double minVal = rawData.reduce((a, b) => a < b ? a : b);
    double maxVal = rawData.reduce((a, b) => a > b ? a : b);
    double range = maxVal - minVal;

    List<int> normalizedData = rawData.map((v) {
      double rel = (v - minVal) / range * 0xFFFF;
      return rel.toInt();
    }).toList();

    // Write to RAW
    Uint8List rawBytes = Uint8List.fromList(Uint16List.fromList(normalizedData).buffer.asUint8List());
    await outputFile.writeAsBytes(rawBytes);

    return outputFilePath;
  }

  /// Converts `.bin` to `.png`
  static Future<String> processBinToPng(String filePath, int size, LanguageProvider langProvider) async {
    final inputFile = File(filePath);
    if (!await inputFile.exists()) {
      throw langProvider.localizedStrings["file_not_found"] ?? "File not found!";
    }

    final outputFilePath = filePath.replaceAll('.bin', '.png');
    final outputFile = File(outputFilePath);

    // Read binary data
    Uint8List bytes = await inputFile.readAsBytes();

    // Check data size
    if (bytes.length != size * size * 4) {
      throw langProvider.localizedStrings["struct_error"] ?? "An error occurred while converting the file. Please check the selected map size.\n\nFor more information, see the help section.";
    }

    ByteData byteData = ByteData.sublistView(bytes);
    List<double> rawData = List.generate(
        size * size, (i) => byteData.getFloat32(i * 4, Endian.little));

    // Normalize data
    double minVal = rawData.reduce((a, b) => a < b ? a : b);
    double maxVal = rawData.reduce((a, b) => a > b ? a : b);
    double range = maxVal - minVal;

    List<int> normalizedData = rawData.map((v) {
      double rel = (v - minVal) / range * 255;
      return rel.toInt();
    }).toList();

    // Create PNG
    Image image = Image(width: size, height: size);
    for (int i = 0; i < size * size; i++) {
      int grayscale = normalizedData[i];
      image.setPixel(
        i % size,
        i ~/ size,
        ColorFloat32.rgba(grayscale, grayscale, grayscale, 255),
      );
    }

    // Save PNG
    await outputFile.writeAsBytes(encodePng(image));

    return outputFilePath;
  }
}
