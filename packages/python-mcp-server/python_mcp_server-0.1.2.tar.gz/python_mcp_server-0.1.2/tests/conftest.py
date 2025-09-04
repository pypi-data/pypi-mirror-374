import time
import subprocess
import sys
from typing import Iterator

from pathlib import Path
import httpx
import pytest
import socket

# Ensure src/ is importable for unit tests (src layout)
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(base_url: str, timeout: float = 20.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(base_url + "/files/download/does_not_exist.txt")
            if r.status_code in (200, 400, 404):
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


@pytest.fixture(scope="session")
def server_proc() -> Iterator[tuple[subprocess.Popen, str]]:
    port = _get_free_port()
    base_url = f"http://127.0.0.1:{port}"
    import os
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("PYTHONUNBUFFERED", "1")
    proc = subprocess.Popen([sys.executable, "main.py", "--port", str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    try:
        ok = _wait_for_server(base_url)
        if not ok:
            # dump logs for debugging
            try:
                out = proc.stdout.read()
                print("--- server logs ---\n" + (out or ""))
            except Exception:
                pass
            raise RuntimeError("server did not start")
        yield proc, base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.fixture(scope="session")
def base_url(server_proc) -> str:  # noqa: ARG001 unused
    _proc, url = server_proc
    return url


@pytest.fixture(scope="session")
def mcp_url(base_url: str) -> str:
    return base_url + "/mcp"
