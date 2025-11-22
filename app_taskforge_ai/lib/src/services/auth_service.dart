import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';

class AuthService extends ChangeNotifier {
  static const _tokenKey = 'auth_token';

  final ApiClient api;
  final SharedPreferences prefs;
  String? _token;

  AuthService._(this.api, this.prefs) {
    _token = prefs.getString(_tokenKey);
    if (_token != null) api.setToken(_token!);
  }

  static Future<AuthService> create(String baseUrl) async {
    final prefs = await SharedPreferences.getInstance();
    final api = ApiClient(baseUrl: baseUrl);
    return AuthService._(api, prefs);
  }

  bool get isAuthenticated => _token != null;
  String? get token => _token;
  ApiClient get client => api;

  Future<bool> login(String email, String password) async {
    final res = await api.post('/auth/login', {'email': email, 'password': password});
    if (res.statusCode == 200) {
      final body = res.body;
      final map = body.isNotEmpty ? jsonDecode(body) : {};
      final t = map['access_token'];
      if (t != null) {
        _token = t;
        api.setToken(t);
        await prefs.setString(_tokenKey, t);
        notifyListeners();
        return true;
      }
    }
    return false;
  }

  Future<void> logout() async {
    _token = null;
    api.setToken('');
    await prefs.remove(_tokenKey);
    notifyListeners();
  }
}
