import 'package:flutter/material.dart';

class ForgeLogo extends StatelessWidget {
  const ForgeLogo({Key? key, this.size = 64}) : super(key: key);
  final double size;

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [BoxShadow(color: Colors.black45, blurRadius: 8, offset: Offset(0, 3))],
          ),
        ),
        Icon(Icons.whatshot, color: Theme.of(context).colorScheme.primary, size: size * 0.6),
      ],
    );
  }
}
