#!/usr/bin/env python3
"""
SubForge - Module execution entry point
Allows running SubForge as: python -m subforge

Created: 2025-09-02 19:59 UTC-3 São Paulo
"""

import sys

# Check if rich CLI is available
try:
    import rich  # noqa: F401
    import typer  # noqa: F401

    # Rich CLI is available, use the advanced interface
    from .cli import main
except ImportError:
    # Fall back to simple CLI
    from .simple_cli import main

if __name__ == "__main__":
    # Allow execution as python -m subforge
    sys.exit(main())