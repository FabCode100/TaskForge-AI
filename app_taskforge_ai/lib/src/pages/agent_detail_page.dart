import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../services/auth_service.dart';

class AgentDetailPage extends StatefulWidget {
  final Map agent;

  const AgentDetailPage({Key? key, required this.agent}) : super(key: key);

  @override
  State<AgentDetailPage> createState() => _AgentDetailPageState();
}

class _AgentDetailPageState extends State<AgentDetailPage> {
  final _inputController = TextEditingController();
  bool _running = false;
  String _status = '';
  String? _result;
  Timer? _pollTimer;
  int? _executionId;

  @override
  void dispose() {
    _pollTimer?.cancel();
    _inputController.dispose();
    super.dispose();
  }

  Future<void> _runAgent() async {
    final auth = Provider.of<AuthService>(context, listen: false);
    final api = auth.client;
    setState(() {
      _running = true;
      _status = 'queued';
      _result = null;
    });

    try {
      // Ensure agent_id is a proper integer
      final rawId = widget.agent['id'] ?? widget.agent['agent_id'];
      int? agentId;
      if (rawId == null) {
        setState(() {
          _status = 'agent id missing';
          _running = false;
        });
        return;
      }
      if (rawId is int) {
        agentId = rawId;
      } else {
        agentId = int.tryParse(rawId.toString());
      }
      if (agentId == null) {
        setState(() {
          _status = 'invalid agent id';
          _running = false;
        });
        return;
      }

      final body = {
        'agent_id': agentId,
        'input': _inputController.text.isEmpty ? null : _inputController.text
      };
      final res = await api.post('/executions', body);
      if (res.statusCode == 200 || res.statusCode == 201) {
        final map = res.body.isNotEmpty ? jsonDecode(res.body) : {};
        _executionId = map['id'] ?? map['execution_id'] ?? map['executionId'];
        if (_executionId != null) {
          _startPolling(_executionId!);
        } else {
          setState(() {
            _status = 'unknown response';
            _running = false;
          });
        }
      } else {
        setState(() {
          _status = 'failed to create execution (${res.statusCode})';
          _running = false;
        });
      }
    } catch (e) {
      setState(() {
        _status = 'error: $e';
        _running = false;
      });
    }
  }

  void _startPolling(int executionId) {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 1), (t) async {
      final auth = Provider.of<AuthService>(context, listen: false);
      final api = auth.client;
      try {
        final res = await api.get('/executions/$executionId');
        if (res.statusCode == 200) {
          final map = res.body.isNotEmpty ? jsonDecode(res.body) : {};
          final status = map['status'] ?? '';
          final result = map['result'];
          setState(() {
            _status = status;
            if (result != null) _result = result is String ? result : jsonEncode(result);
          });
          if (status == 'completed' || status == 'failed') {
            _pollTimer?.cancel();
            setState(() {
              _running = false;
            });
          }
        } else {
          // ignore for now
        }
      } catch (e) {
        // ignore polling errors
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final agent = widget.agent;
    return Scaffold(
      appBar: AppBar(
        title: Text(agent['name'] ?? 'Agent'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(agent['name'] ?? '', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 8),
                    Text(agent['description'] ?? '', style: Theme.of(context).textTheme.bodyMedium),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _inputController,
              decoration: const InputDecoration(labelText: 'Input'),
              minLines: 1,
              maxLines: 4,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _running ? null : _runAgent,
                  icon: const Icon(Icons.play_arrow),
                  label: Text(_running ? 'Running...' : 'Run'),
                ),
                const SizedBox(width: 12),
                if (_status.isNotEmpty) Text('Status: $_status')
              ],
            ),
            const SizedBox(height: 12),
            if (_result != null)
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: SingleChildScrollView(child: Text(_result!)),
                  ),
                ),
              )
            else
              const SizedBox.shrink()
          ],
        ),
      ),
    );
  }
}
