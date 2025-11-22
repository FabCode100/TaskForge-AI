import 'package:flutter/material.dart';
import 'theme/forge_theme.dart';
import 'pages/agents_list_page.dart';

class TaskForgeApp extends StatelessWidget {
  const TaskForgeApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TaskForge',
      theme: ForgeTheme.lightTheme,
      darkTheme: ForgeTheme.darkTheme,
      themeMode: ThemeMode.dark,
      home: const AgentsListPage(),
    );
  }
}
