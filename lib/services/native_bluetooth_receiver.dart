import 'package:flutter/services.dart';

class NativeBluetoothReceiver {
  static const MethodChannel _channel = MethodChannel('gt_bluetooth_channel');

  static Future<String?> startReceiver() async {
    try {
      final result = await _channel.invokeMethod<String>('startBluetoothReceiver');
      return result;
    } on PlatformException catch (e) {
      return "Erreur : \${e.message}";
    }
  }
}