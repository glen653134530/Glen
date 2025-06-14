import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

class ExplorerPage extends StatefulWidget {
  const ExplorerPage({super.key});

  @override
  State<ExplorerPage> createState() => _ExplorerPageState();
}

class _ExplorerPageState extends State<ExplorerPage> {
  List<FileSystemEntity> files = [];

  @override
  void initState() {
    super.initState();
    _loadFiles();
  }

  Future<void> _loadFiles() async {
    final directory = await getApplicationDocumentsDirectory();
    final dir = Directory(directory.path);
    final fileList = dir.listSync();
    setState(() {
      files = fileList;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Fichiers reçus")),
      body: files.isEmpty
          ? const Center(child: Text("Aucun fichier reçu pour l’instant"))
          : ListView.builder(
              itemCount: files.length,
              itemBuilder: (context, index) {
                final file = files[index];
                final fileName = file.path.split('/').last;
                return ListTile(
                  leading: const Icon(Icons.insert_drive_file),
                  title: Text(fileName),
                  subtitle: Text(file.path),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () {
                      File(file.path).deleteSync();
                      _loadFiles();
                    },
                  ),
                );
              },
            ),
    );
  }
}