import 'dart:convert';
import 'package:http/http.dart' as http;

const String _baseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

class ApiService {
  final String token;
  ApiService({required this.token});

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      };

  Future<Map<String, dynamic>?> getStats() async {
    try {
      final res = await http.get(Uri.parse('$_baseUrl/stats'), headers: _headers);
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (_) {}
    return null;
  }

  Future<List<dynamic>> getCallLogs({int limit = 20}) async {
    try {
      final res = await http.get(
        Uri.parse('$_baseUrl/call-logs?limit=$limit'),
        headers: _headers,
      );
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (_) {}
    return [];
  }

  Future<Map<String, dynamic>?> analyzeText(String transcript) async {
    try {
      final res = await http.post(
        Uri.parse('$_baseUrl/analyze'),
        headers: _headers,
        body: jsonEncode({'transcript': transcript}),
      );
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (_) {}
    return null;
  }
}
