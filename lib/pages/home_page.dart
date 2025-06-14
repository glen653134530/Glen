import 'package:flutter/material.dart';
import 'send_page.dart';
import 'receive_page.dart';
import 'explorer_page.dart';
import 'history_page.dart';
import 'bluetooth_page.dart';
import 'bluetooth_receive_page.dart';

class HomePage extends StatelessWidget {
  final VoidCallback? openSettings;
  const HomePage({super.key, this.openSettings});
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F5F9),
      body: Column(
        children: [
          Align(
            alignment: Alignment.topRight,
            child: IconButton(
              icon: const Icon(Icons.settings),
              onPressed: openSettings,
            ),
          ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.send_to_mobile, size: 100, color: Colors.blueAccent),
            const SizedBox(height: 30),
            Text("GT FileShare",
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.blueAccent)),
            const SizedBox(height: 40),
            ElevatedButton.icon(
              icon: const Icon(Icons.send),
              label: const Text("Envoyer un fichier"),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SendPage())),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.folder_open),
              label: const Text("Voir fichiers reçus"),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.history),
              label: const Text("Historique"),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.bluetooth),
              label: const Text("Bluetooth"),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.bluetooth_audio),
              label: const Text("Recevoir via Bluetooth"),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BluetoothReceivePage())),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BluetoothPage())),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const HistoryPage())),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ExplorerPage())),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.download),
              label: const Text("Recevoir un fichier"),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SendPage())),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
              ),
            )
          ],
        ),
      ),
    );
  }
}