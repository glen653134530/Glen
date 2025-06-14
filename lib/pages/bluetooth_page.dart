import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:permission_handler/permission_handler.dart';
import '../services/file_transfer_service.dart';

class BluetoothPage extends StatefulWidget {
  const BluetoothPage({super.key});

  @override
  State<BluetoothPage> createState() => _BluetoothPageState();
}

class _BluetoothPageState extends State<BluetoothPage> {
  List<BluetoothDevice> _devices = [];
  bool _isScanning = false;

  @override
  void initState() {
    super.initState();
    _initBluetooth();
  }

  Future<void> _initBluetooth() async {
    await Permission.bluetooth.request();
    await Permission.bluetoothConnect.request();
    await Permission.bluetoothScan.request();

    final isEnabled = await FlutterBluetoothSerial.instance.isEnabled;
    if (!isEnabled!) {
      await FlutterBluetoothSerial.instance.requestEnable();
    }

    setState(() {
      _isScanning = true;
    });

    final bondedDevices = await FlutterBluetoothSerial.instance.getBondedDevices();
    setState(() {
      _devices = bondedDevices.toList();
      _isScanning = false;
    });
  }

  void _connectToDevice(BluetoothDevice device) async {
    try {
      final connection = await BluetoothConnection.toAddress(device.address);
      setState(() {});
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Connecté à ${device.name}")),
      );

      // Envoi du fichier sélectionné
      final filePath = await FileTransferService().pickFile();
      if (filePath == null || filePath.path == null) return;
      final file = File(filePath.path!);
      if (!file.existsSync()) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Fichier introuvable.")),
        );
        return;
      }

      final bytes = file.readAsBytesSync();
      connection.output.add(bytes);
      await connection.output.allSent;
      connection.output.add(utf8.encode("Bonjour depuis GT FileShare !\n"));
      await connection.output.allSent;
      connection.finish(); // Ferme la connexion
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Erreur de connexion à ${device.name}")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Transfert Bluetooth")),
      body: _isScanning
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _devices.length,
              itemBuilder: (context, index) {
                final device = _devices[index];
                return ListTile(
                  leading: const Icon(Icons.bluetooth),
                  title: Text(device.name ?? "Appareil inconnu"),
                  subtitle: Text(device.address),
                  trailing: ElevatedButton(
                    child: const Text("Envoyer"),
                    onPressed: () => _connectToDevice(device),
                  ),
                );
              },
            ),
    );
  }
}