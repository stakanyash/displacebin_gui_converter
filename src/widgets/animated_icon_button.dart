import 'package:flutter/material.dart';

class AnimatedIconButton extends StatefulWidget {
  final IconData defaultIcon;
  final IconData hoverIcon;
  final VoidCallback onPressed;
  final double size;
  final Color color;

  const AnimatedIconButton({
    required this.defaultIcon,
    required this.hoverIcon,
    required this.onPressed,
    this.size = 25.0,
    this.color = Colors.black,
    Key? key,
  }) : super(key: key);

  @override
  _AnimatedIconButtonState createState() => _AnimatedIconButtonState();
}

class _AnimatedIconButtonState extends State<AnimatedIconButton> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: IconButton(
        onPressed: widget.onPressed,
        icon: AnimatedSwitcher(
          duration: Duration(milliseconds: 200),
          transitionBuilder: (child, animation) => ScaleTransition(
            scale: animation,
            child: child,
          ),
          child: Icon(
            _isHovered ? widget.hoverIcon : widget.defaultIcon,
            key: ValueKey<bool>(_isHovered),
            size: widget.size,
            color: widget.color,
          ),
        ),
      ),
    );
  }
}
