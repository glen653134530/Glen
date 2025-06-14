import 'package:flutter/material.dart';
import '../services/history_service.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  List<String> history = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  void _loadHistory() async {
    final data = await HistoryService.getHistory();
    setState(() {
      history = data;
    });
  }

  void _clearHistory() async {
    await HistoryService.clearHistory();
    _loadHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Historique"),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_forever),
            onPressed: _clearHistory,
          )
        ],
      ),
      body: history.isEmpty
          ? const Center(child: Text("Aucun transfert enregistré."))
          : ListView.builder(
              itemCount: history.length,
              itemBuilder: (context, index) {
                return ListTile(
                  leading: const Icon(Icons.history),
                  title: Text(history[index]),
                );
              },
            ),
    );
  }
}