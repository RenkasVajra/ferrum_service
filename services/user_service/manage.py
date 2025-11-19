#!/usr/bin/env python3
"""Management utility for user_service."""

import os
import sys
from pathlib import Path


def main() -> None:
    sys.path.append(str(Path(__file__).resolve().parent / "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_service.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Не удалось импортировать Django.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

