import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

import 'src/app.dart';
import 'src/services/auth_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Choose backend base URL depending on platform:
  // - Web (Edge/Chrome): use localhost
  // - Mobile (emulator): use 10.0.2.2 for Android emulator
  final baseUrl = kIsWeb ? 'http://localhost:8000/api/v1' : 'http://10.0.2.2:8000/api/v1';
  debugPrint('Using backend baseUrl: $baseUrl');
  final auth = await AuthService.create(baseUrl);
  runApp(ChangeNotifierProvider<AuthService>.value(
    value: auth,
    child: const TaskForgeApp(),
  ));
}
