import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:qr_code_scanner/qr_code_scanner.dart';
import '../services/file_transfer_service.dart';
import '../services/history_service.dart';

class SendPage extends StatefulWidget {
  const SendPage({super.key});

  @override
  State<SendPage> createState() => _SendPageState();
}

class _SendPageState extends State<SendPage> {
  void _scanNetwork() async {
    setState(() {
      isScanning = true;
    });

    final localIp = await _getLocalIp();
    if (localIp == null) return;

    final subnet = localIp.substring(0, localIp.lastIndexOf('.') + 1);
    for (int i = 1; i < 255; i++) {
      final testIp = '$subnet$i';
      if (ipList.contains(testIp)) continue;
      try {
        final uri = Uri.parse('http://$testIp:8080');
        final response = await http.get(uri).timeout(const Duration(milliseconds: 500));
        if (response.statusCode == 405 || response.statusCode == 200) {
          setState(() {
            ipList.add(testIp);
          });
        }
      } catch (_) {}
    }

    setState(() {
      isScanning = false;
    });
  }

  Future<String?> _getLocalIp() async {
    for (var interface in await NetworkInterface.list()) {
      for (var addr in interface.addresses) {
        if (addr.type == InternetAddressType.IPv4 &&
            !addr.isLoopback &&
            addr.address.startsWith('192.')) {
          return addr.address;
        }
      }
    }
    return null;
  }
  String? selectedFile;
  String? filePath;
  String? status;
  final TextEditingController ipController = TextEditingController();
  List<String> ipList = [];
  bool isScanning = false;

  void _selectFile() async {
    final service = FileTransferService();
    final file = await service.pickFile();
    if (file != null) {
      setState(() {
        selectedFile = file.name;
        filePath = file.path;
        status = null;
      });
    }
  }

  void _addIp() {
    final ip = ipController.text.trim();
    if (ip.isNotEmpty && !ipList.contains(ip)) {
      setState(() {
        ipList.add(ip);
        ipController.clear();
      });
    }
  }

  void _sendFile() async {
    if (filePath == null || ipList.isEmpty) return;

    for (var ip in ipList) {
      try {
        final uri = Uri.parse("http://$ip:8080?filename=$selectedFile");
        final request = http.MultipartRequest('POST', uri)
          ..files.add(await http.MultipartFile.fromPath('file', filePath!));
        final response = await request.send();
        await HistoryService.addToHistory(
          response.statusCode == 200
              ? "Envoyé avec succès à $ip"
              : "Échec de l'envoi à $ip",
        );
      } catch (e) {
        await HistoryService.addToHistory("Erreur lors de l'envoi à $ip");
      }
    }

    setState(() {
      status = "Envoi terminé.";
    });
  }

  void _scanQrCode() async {
    final result = await Navigator.push(context, MaterialPageRoute(builder: (_) => const QrScannerPage()));
    if (result != null && result is String && !ipList.contains(result)) {
      setState(() {
        ipList.add(result);
      });
    }
  }

  void _removeIp(String ip) {
    setState(() {
      ipList.remove(ip);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Envoyer un fichier")),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            ElevatedButton.icon(
              icon: const Icon(Icons.folder),
              label: const Text("Choisir un fichier"),
              onPressed: _selectFile,
            ),
            const SizedBox(height: 20),
            if (selectedFile != null)
              Text("Fichier sélectionné : $selectedFile", style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 20),
            TextField(
              controller: ipController,
              decoration: InputDecoration(
                labelText: "Adresse IP",
                suffixIcon: IconButton(
                  icon: const Icon(Icons.add),
                  onPressed: _addIp,
                ),
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            ElevatedButton.icon(
              icon: const Icon(Icons.wifi_find),
              label: const Text("Scanner le réseau local"),
              onPressed: _scanNetwork,
            ),
            const SizedBox(height: 10),
            ElevatedButton.icon(
              icon: const Icon(Icons.qr_code_scanner),
              label: const Text("Scanner un QR Code"),
              onPressed: _scanQrCode,
            ),
            const SizedBox(height: 10),
            ElevatedButton.icon(
              icon: const Icon(Icons.wifi_find),
              label: const Text("Scanner le réseau local"),
              onPressed: _scanNetwork,
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              children: ipList.map((ip) {
                return Chip(
                  label: Text(ip),
                  onDeleted: () => _removeIp(ip),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.send),
              label: const Text("Envoyer à tous"),
              onPressed: _sendFile,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            ),
            if (status != null) ...[
              const SizedBox(height: 20),
              Text(status!, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ]
          ],
        ),
      ),
    );
  }
}

class QrScannerPage extends StatefulWidget {
  const QrScannerPage({super.key});

  @override
  State<QrScannerPage> createState() => _QrScannerPageState();
}

class _QrScannerPageState extends State<QrScannerPage> {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? controller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Scanner un QR Code")),
      body: QRView(
        key: qrKey,
        onQRViewCreated: _onQRViewCreated,
      ),
    );
  }

  void _onQRViewCreated(QRViewController controller) {
    this.controller = controller;
    controller.scannedDataStream.listen((scanData) {
      controller.pauseCamera();
      Navigator.pop(context, scanData.code);
    });
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }
}