import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'src/app.dart';
import 'src/services/auth_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final auth = await AuthService.create('http://10.0.2.2:8000/api/v1'); // Android emulator localhost
  runApp(ChangeNotifierProvider<AuthService>.value(
    value: auth,
    child: const TaskForgeApp(),
  ));
}
