import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'package:image/image.dart';

class FileProcessor {
  /// Конвертирует `.bin` в `.raw`
  static Future<String> processBinToRaw(String filePath, int size) async {
    final inputFile = File(filePath);
    if (!await inputFile.exists()) {
      throw "Файл не найден!";
    }

    final outputFilePath = filePath.replaceAll('.bin', '.raw');
    final outputFile = File(outputFilePath);

    // Читаем бинарные данные
    Uint8List bytes = await inputFile.readAsBytes();
    ByteData byteData = ByteData.sublistView(bytes);
    List<double> rawData = List.generate(size * size, (i) => byteData.getFloat32(i * 4, Endian.little));

    // Нормализация данных
    double minVal = rawData.reduce((a, b) => a < b ? a : b);
    double maxVal = rawData.reduce((a, b) => a > b ? a : b);
    double range = maxVal - minVal;

    List<int> normalizedData = rawData.map((v) {
      double rel = (v - minVal) / range * 0xFFFF;
      return rel.toInt();
    }).toList();

    // Запись в RAW
    Uint8List rawBytes = Uint8List.fromList(Uint16List.fromList(normalizedData).buffer.asUint8List());
    await outputFile.writeAsBytes(rawBytes);

    return outputFilePath;
  }

  /// Конвертирует `.bin` в `.png`
  static Future<String> processBinToPng(String filePath, int size) async {
    final inputFile = File(filePath);
    if (!await inputFile.exists()) {
      throw "Файл не найден!";
    }

    final outputFilePath = filePath.replaceAll('.bin', '.png');
    final outputFile = File(outputFilePath);

    // Читаем бинарные данные
    Uint8List bytes = await inputFile.readAsBytes();
    ByteData byteData = ByteData.sublistView(bytes);
    List<double> rawData = List.generate(
        size * size, (i) => byteData.getFloat32(i * 4, Endian.little));

    // Нормализация данных
    double minVal = rawData.reduce((a, b) => a < b ? a : b);
    double maxVal = rawData.reduce((a, b) => a > b ? a : b);
    double range = maxVal - minVal;

    List<int> normalizedData = rawData.map((v) {
      double rel = (v - minVal) / range * 255;
      return rel.toInt();
    }).toList();

    // Создание PNG
    Image image = Image(width: size, height: size);
    for (int i = 0; i < size * size; i++) {
      int grayscale = normalizedData[i];
      // Создаем объект Color с явным указанием каналов
      image.setPixel(
        i % size, 
        i ~/ size, 
        ColorFloat32.rgba(grayscale, grayscale, grayscale, 255),
      );
    }

    // Сохранение PNG
    await outputFile.writeAsBytes(encodePng(image));

    return outputFilePath;
  }
}