import 'package:file_picker/file_picker.dart';

class FileTransferService {
  Future<PlatformFile?> pickFile() async {
    final result = await FilePicker.platform.pickFiles();
    if (result != null && result.files.isNotEmpty) {
      return result.files.first;
    }
    return null;
  }
}