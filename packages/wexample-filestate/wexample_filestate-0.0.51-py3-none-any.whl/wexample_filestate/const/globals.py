from __future__ import annotations

NAME_PATTERN_ANY_ITEM = "^(?!\\.\\.$)(?!^\\.$).+$"  # Ignore . and ..
NAME_PATTERN_NO_LEADING_DOT = "^(?!\\.).+$"  # Ignore every name starting with a dot
