import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:provider/provider.dart';

import '../services/auth_service.dart';
import 'agent_detail_page.dart';

class AgentsListPage extends StatefulWidget {
  const AgentsListPage({Key? key}) : super(key: key);

  @override
  State<AgentsListPage> createState() => _AgentsListPageState();
}

class _AgentsListPageState extends State<AgentsListPage> {
  List agents = [];
  bool loading = false;

  @override
  void initState() {
    super.initState();
    fetchAgents();
  }

  Future<void> fetchAgents() async {
    setState(() => loading = true);
    final auth = Provider.of<AuthService>(context, listen: false);
    final api = auth.client;
    try {
      final res = await api.get('/agents/');
      if (res.statusCode == 200) {
        final body = res.body;
        final decoded = body.isNotEmpty ? jsonDecode(body) : [];
        setState(() {
          agents = List.from(decoded ?? []);
        });
      }
    } catch (e) {
      // ignore
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TaskForge Agents'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: fetchAgents,
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            Expanded(
              child: loading
                  ? const Center(child: CircularProgressIndicator())
                  : GridView.builder(
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        childAspectRatio: 3 / 2,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                      ),
                      itemCount: agents.length == 0 ? 6 : agents.length,
                      itemBuilder: (context, index) {
                        final a = agents.isEmpty
                          ? {"id": 1, "name": "Demo Agent", "description": "Smart automation agent"}
                          : agents[index];
                        return Card(
                          child: InkWell(
                            onTap: () {
                              Navigator.of(context).push(MaterialPageRoute(
                                  builder: (_) => AgentDetailPage(agent: a)));
                            },
                            child: Padding(
                              padding: const EdgeInsets.all(12.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(a['name'], style: Theme.of(context).textTheme.titleLarge),
                                  const SizedBox(height: 8),
                                  Text(a['description'] ?? '', style: Theme.of(context).textTheme.bodyMedium),
                                  const Spacer(),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      ElevatedButton(
                                          onPressed: () {
                                            Navigator.of(context).push(MaterialPageRoute(
                                                builder: (_) => AgentDetailPage(agent: a)));
                                          },
                                          child: const Text('Run'))
                                    ],
                                  )
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: const Icon(Icons.add),
      ),
    );
  }
}
