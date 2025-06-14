import 'package:flutter/material.dart';
import '../services/native_bluetooth_receiver.dart';

class BluetoothReceivePage extends StatefulWidget {
  const BluetoothReceivePage({super.key});

  @override
  State<BluetoothReceivePage> createState() => _BluetoothReceivePageState();
}

class _BluetoothReceivePageState extends State<BluetoothReceivePage> {
  String status = "Appuye sur le bouton ci-dessous pour démarrer la réception...";

  void _startReceiver() async {
    setState(() {
      status = "En attente de connexion Bluetooth...";
    });
    final result = await NativeBluetoothReceiver.startReceiver();
    setState(() {
      status = result ?? "Réception terminée.";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Réception Bluetooth")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(status, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.bluetooth_audio),
              label: const Text("Démarrer la réception"),
              onPressed: _startReceiver,
            )
          ],
        ),
      ),
    );
  }
}