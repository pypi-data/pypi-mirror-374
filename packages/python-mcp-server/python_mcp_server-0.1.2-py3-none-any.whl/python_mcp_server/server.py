"""Entry points for python-mcp-server.

Exposes a `main()` function used by the console script and `python -m`.
"""

from .app import run_http


def main() -> None:
    run_http()


if __name__ == "__main__":  # pragma: no cover
    main()
