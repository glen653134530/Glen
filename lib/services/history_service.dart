import 'package:shared_preferences/shared_preferences.dart';

class HistoryService {
  static const String _historyKey = 'file_history';

  static Future<List<String>> getHistory() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_historyKey) ?? [];
  }

  static Future<void> addToHistory(String entry) async {
    final prefs = await SharedPreferences.getInstance();
    final history = prefs.getStringList(_historyKey) ?? [];
    history.insert(0, entry);
    await prefs.setStringList(_historyKey, history.take(50).toList());
  }

  static Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_historyKey);
  }
}