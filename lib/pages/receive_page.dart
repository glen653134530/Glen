import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../services/history_service.dart';
import '../services/qr_service.dart';

class ReceivePage extends StatefulWidget {
  const ReceivePage({super.key});

  @override
  State<ReceivePage> createState() => _ReceivePageState();
}

class _ReceivePageState extends State<ReceivePage> {
  HttpServer? _server;
  String? _status;
  String? _localIp;

  @override
  void initState() {
    super.initState();
    _startServer();
  }

  Future<void> _startServer() async {
    final directory = await getApplicationDocumentsDirectory();
    final address = InternetAddress.anyIPv4;
    final server = await HttpServer.bind(address, 8080);

    final ip = await QrService.getLocalIpAddress();

    await HistoryService.addToHistory('Reçu : \$filename');
        setState(() {
      _server = server;
      _localIp = ip;
      _status = "Serveur prêt à recevoir sur : http://$ip:8080";
    });

    server.listen((HttpRequest request) async {
      if (request.method == 'POST') {
        final filename = request.uri.queryParameters['filename'] ?? 'fichier_recu';
        final file = File('${directory.path}/$filename');
        await request.pipe(file.openWrite());
        setState(() {
          _status = "Fichier reçu : $filename";
        });
        request.response.write('OK');
        await request.response.close();
      } else {
        request.response.statusCode = HttpStatus.methodNotAllowed;
        await request.response.close();
      }
    });
  }

  @override
  void dispose() {
    _server?.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Recevoir un fichier")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (_localIp != null)
                QrImageView(
                  data: _localIp!,
                  version: QrVersions.auto,
                  size: 200.0,
                ),
              const SizedBox(height: 20),
              Text(_status ?? "Démarrage du serveur...",
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 16)),
            ],
          ),
        ),
      ),
    );
  }
}