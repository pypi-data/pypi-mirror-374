import asyncio
import base64
import atexit
import uuid
import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from jupyter_client.manager import KernelManager
from starlette.responses import FileResponse, JSONResponse
from starlette.requests import Request

from fastmcp import FastMCP, Context


class KernelManagerSingleton:
    """Singleton wrapper around a Jupyter kernel client.

    Starts a single ipykernel instance per process and provides access to the
    connected client. The kernel is shut down automatically on interpreter
    exit via ``atexit``.
    """
    _instance = None
    _km: Optional[KernelManager] = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KernelManagerSingleton, cls).__new__(cls)
            cls._km = KernelManager()
            cls._km.start_kernel()
            cls._client = cls._km.client()
            cls._client.start_channels()
            atexit.register(cls._instance.shutdown_kernel)
        return cls._instance

    def get_client(self):
        return self._client

    def shutdown_kernel(self):
        if self._km and self._km.is_alive():
            self._km.shutdown_kernel(now=True)


def _ensure_within_workspace(workspace: Path, p: Path) -> Path:
    """Resolve ``p`` and assert it stays within ``workspace``.

    Args:
      workspace: Absolute path to the server's workspace root.
      p: Input path (absolute or relative) to validate.

    Returns:
      A resolved path guaranteed to be within ``workspace``.

    Raises:
      ValueError: If the resolved path would escape the workspace.
    """
    p = (workspace / p).resolve() if not p.is_absolute() else p.resolve()
    if workspace not in p.parents and p != workspace:
        raise ValueError("Path escapes workspace")
    return p


def _render_tree(root: Path, max_depth: Optional[int] = 3, include_files: bool = True, include_dirs: bool = True) -> str:
    """Render an ASCII tree of a directory subtree.

    Args:
      root: Root directory to render.
      max_depth: Limit traversal depth (None for unlimited).
      include_files: Include files in the output tree.
      include_dirs: Include directories in the output tree.

    Returns:
      Textual tree representation using box-drawing characters.
    """
    def is_included(p: Path) -> bool:
        return (include_files and p.is_file()) or (include_dirs and p.is_dir())

    def children(p: Path):
        try:
            return sorted([c for c in p.iterdir() if is_included(c)], key=lambda x: (x.is_file(), x.name.lower()))
        except Exception:
            return []

    lines: list[str] = []

    def walk(p: Path, prefix: str = "", depth: int = 0):
        if depth == 0:
            lines.append(p.name + ("/" if p.is_dir() else ""))
        if max_depth is not None and depth >= max_depth:
            return
        kids = children(p)
        for i, c in enumerate(kids):
            last = i == len(kids) - 1
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + c.name + ("/" if c.is_dir() else ""))
            if c.is_dir():
                extension = "    " if last else "│   "
                walk(c, prefix + extension, depth + 1)

    walk(root)
    return "\n".join(lines)


def create_app(workspace_dir: Optional[Path] = None, name: str = "Python MCP Server") -> FastMCP:
    """Create a FastMCP application instance.

    The app exposes tools for executing Python in a persistent Jupyter kernel,
    managing files and scripts, installing dependencies, and basic inspection.

    Args:
      workspace_dir: Optional workspace location; defaults to ``$MCP_WORKSPACE_DIR``
        or ``./workspace`` when unset.
      name: Human-friendly server name shown in FastMCP banner.

    Returns:
      A configured FastMCP application ready to ``run(transport="http", ...)``.
    """
    workspace = Path(os.environ.get("MCP_WORKSPACE_DIR", "workspace")).resolve() if workspace_dir is None else Path(workspace_dir).resolve()
    scripts_dir = (workspace / "scripts").resolve()
    outputs_dir = (workspace / "outputs").resolve()
    uploads_dir = (workspace / "uploads").resolve()
    for d in (workspace, scripts_dir, outputs_dir, uploads_dir):
        d.mkdir(parents=True, exist_ok=True)

    kernel_manager = KernelManagerSingleton()

    def snapshot_workspace_files() -> set[str]:
        return {
            str(p.relative_to(workspace))
            for p in workspace.rglob("*")
            if p.is_file()
        }

    app = FastMCP(name=name)

    @app.tool
    async def run_python_code(ctx: Context, code: str) -> dict:  # noqa: ARG001
        """Execute Python code in the persistent Jupyter kernel.

        The kernel session is shared across calls, enabling stateful workflows.
        Rich display outputs (``image/png``, ``image/svg+xml``, ``application/json``)
        are saved under ``outputs/`` and their relative paths are returned.

        Args:
          ctx: FastMCP request context (unused).
          code: Python source to execute.

        Returns:
          Dict with keys ``stdout``, ``stderr``, ``results`` (text results),
          ``outputs`` (saved display artifacts), and ``new_files`` (workspace changes).
        """
        client = kernel_manager.get_client()
        while True:
            try:
                client.get_shell_msg(timeout=0.1)
            except Exception:
                break
        before_files = snapshot_workspace_files()
        msg_id = client.execute(code)
        stdout = ""
        stderr = ""
        outputs: list[str] = []
        results: list[str] = []
        while True:
            try:
                msg = client.get_iopub_msg(timeout=1)
                if msg['parent_header']['msg_id'] != msg_id:
                    continue
                msg_type = msg['header']['msg_type']
                if msg_type == 'status' and msg['content']['execution_state'] == 'idle':
                    break
                elif msg_type == 'stream':
                    if msg['content']['name'] == 'stdout':
                        stdout += msg['content']['text']
                    else:
                        stderr += msg['content']['text']
                elif msg_type in ('display_data', 'execute_result'):
                    data = msg['content']['data']
                    if 'image/png' in data:
                        img_data = base64.b64decode(data['image/png'])
                        filename = f"{uuid.uuid4()}.png"
                        filepath = outputs_dir / filename
                        with open(filepath, "wb") as f:
                            f.write(img_data)
                        outputs.append(str(filepath.relative_to(workspace)))
                    elif 'image/svg+xml' in data:
                        svg_text = data['image/svg+xml']
                        filename = f"{uuid.uuid4()}.svg"
                        filepath = outputs_dir / filename
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(svg_text)
                        outputs.append(str(filepath.relative_to(workspace)))
                    if 'application/json' in data:
                        try:
                            parsed = data['application/json']
                            filename = f"{uuid.uuid4()}.json"
                            filepath = outputs_dir / filename
                            with open(filepath, "w", encoding="utf-8") as f:
                                json.dump(parsed, f)
                            outputs.append(str(filepath.relative_to(workspace)))
                        except Exception:
                            pass
                    if 'text/plain' in data:
                        results.append(str(data['text/plain']))
                elif msg_type == 'error':
                    stderr += "\n".join(msg['content']['traceback'])
            except asyncio.TimeoutError:
                break
            except Exception as e:
                stderr += f"Error processing kernel message: {e}"
                break
        after_files = snapshot_workspace_files()
        new_files = sorted(list(after_files - before_files))
        return {"stdout": stdout, "stderr": stderr, "results": results, "outputs": outputs, "new_files": new_files}

    @app.tool
    async def code_completion(ctx: Context, code: str, cursor_pos: int) -> dict:  # noqa: ARG001
        """Request code completion suggestions from the kernel.

        Args:
          ctx: FastMCP request context (unused).
          code: Buffer contents to complete against.
          cursor_pos: Cursor index within ``code`` to complete at.

        Returns:
          Raw Jupyter completion reply content.
        """
        client = kernel_manager.get_client()
        client.complete(code, cursor_pos)
        msg = client.get_shell_msg(timeout=1)
        return msg['content']

    @app.tool
    async def inspect_object(ctx: Context, code: str, cursor_pos: int, detail_level: int = 0) -> dict:  # noqa: ARG001
        """Inspect an object/expression within the kernel namespace.

        Args:
          ctx: FastMCP request context (unused).
          code: Buffer containing the target expression.
          cursor_pos: Cursor index of the expression to inspect.
          detail_level: Jupyter detail level (0 minimal; higher is more verbose).

        Returns:
          Raw Jupyter inspection reply content.
        """
        client = kernel_manager.get_client()
        client.inspect(code, cursor_pos, detail_level)
        msg = client.get_shell_msg(timeout=1)
        return msg['content']

    @app.tool
    async def list_files(
        ctx: Context,
        path: str | None = None,
        recursive: bool = False,
        tree: bool = False,
        max_depth: int | None = 3,
        include_files: bool = True,
        include_dirs: bool = True,
    ) -> dict:  # noqa: ARG001
        """List workspace files and directories.

        Args:
          ctx: FastMCP request context (unused).
          path: Optional relative path under the workspace root.
          recursive: If True, return all descendants in a flat list (``files``).
          tree: If True, return an ASCII tree rendering (``tree``).
          max_depth: Depth cap for recursion/tree; None for unlimited.
          include_files: Include files in results.
          include_dirs: Include directories in results.

        Returns:
          Flat listing: ``{"root": str, "files": list[str]}``
          Tree: ``{"root": str, "tree": str}``
          On error: ``{"error": str}``.
        """
        try:
            base = _ensure_within_workspace(workspace, Path(path or "."))
        except Exception:
            return {"error": "Invalid path"}
        if tree:
            root = base
            if not root.exists():
                return {"error": "Path not found"}
            if root.is_file():
                rel = root.relative_to(workspace)
                return {"root": str(rel), "tree": rel.name}
            txt = _render_tree(root, max_depth=max_depth, include_files=include_files, include_dirs=include_dirs)
            return {"root": str(base.relative_to(workspace)), "tree": txt}
        if not base.exists():
            return {"error": "Path not found"}
        if recursive:
            results: list[str] = []
            for p in base.rglob("*"):
                if not ((include_files and p.is_file()) or (include_dirs and p.is_dir())):
                    continue
                if max_depth is not None:
                    try:
                        depth = len(p.relative_to(base).parts)
                    except Exception:
                        depth = 0
                    if depth > max_depth:
                        continue
                results.append(str(p.relative_to(workspace)))
            return {"root": str(base.relative_to(workspace)) if base != workspace else ".", "files": sorted(results)}
        else:
            try:
                entries = [
                    str((base / c.name).relative_to(workspace))
                    for c in base.iterdir()
                    if (include_files and c.is_file()) or (include_dirs and c.is_dir())
                ]
            except Exception as e:
                return {"error": str(e)}
            return {"root": str(base.relative_to(workspace)) if base != workspace else ".", "files": sorted(entries)}

    @app.tool
    async def ping(ctx: Context) -> dict:  # noqa: ARG001
        """Lightweight server health check.

        Args:
          ctx: FastMCP request context (unused).

        Returns:
          ``{"ok": True}`` if the server is responsive.
        """
        return {"ok": True}

    @app.tool
    async def delete_file(ctx: Context, filename: str) -> dict:  # noqa: ARG001
        """Delete a file under the workspace.

        Args:
          ctx: FastMCP request context (unused).
          filename: Relative path of the file to delete.

        Returns:
          JSONResponse with ``{"success": True}`` or an error with status code.
        """
        try:
            filepath = _ensure_within_workspace(workspace, Path(filename))
        except Exception:
            return JSONResponse({"error": "Invalid path"}, status_code=400)
        if not filepath.exists():
            return JSONResponse({"error": "File not found"}, status_code=404)
        try:
            os.remove(filepath)
            return JSONResponse({"success": True})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.tool
    async def read_file(ctx: Context, path: str, max_bytes: int | None = None) -> dict:  # noqa: ARG001
        """Read a text or binary file from the workspace.

        Attempts UTF-8 decoding; on failure, returns base64-encoded bytes.

        Args:
          ctx: FastMCP request context (unused).
          path: Relative path to read.
          max_bytes: Optional cap on bytes read.

        Returns:
          ``{"text": str}`` for UTF-8, or ``{"base64": str}`` for binary; or ``{"error": str}``.
        """
        try:
            p = _ensure_within_workspace(workspace, Path(path))
        except Exception:
            return {"error": "Invalid path"}
        if not p.exists() or not p.is_file():
            return {"error": "File not found"}
        try:
            data = p.read_bytes()
            if max_bytes is not None and len(data) > max_bytes:
                data = data[:max_bytes]
            try:
                text = data.decode("utf-8")
                return {"text": text}
            except UnicodeDecodeError:
                return {"base64": base64.b64encode(data).decode("ascii")}
        except Exception as e:
            return {"error": str(e)}

    @app.tool
    async def write_file(ctx: Context, path: str, content: str | None = None, base64_content: str | None = None) -> dict:  # noqa: ARG001
        """Write a file under the workspace.

        Args:
          ctx: FastMCP request context (unused).
          path: Relative path to write.
          content: Text content to write (UTF-8).
          base64_content: Base64-encoded bytes to write; takes precedence over ``content``.

        Returns:
          ``{"path": str}`` of the written file, or ``{"error": str}``.
        """
        try:
            p = _ensure_within_workspace(workspace, Path(path))
        except Exception:
            return {"error": "Invalid path"}
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            if base64_content is not None:
                p.write_bytes(base64.b64decode(base64_content))
            else:
                p.write_text(content or "", encoding="utf-8")
            return {"path": str(p.relative_to(workspace))}
        except Exception as e:
            return {"error": str(e)}

    @app.tool
    async def save_script(ctx: Context, name: str, content: str) -> dict:  # noqa: ARG001
        """Save a Python script into ``scripts/`` under the workspace.

        Args:
          ctx: FastMCP request context (unused).
          name: Script base name (``.py`` appended if missing).
          content: Script source code.

        Returns:
          ``{"script": str}`` relative path to the saved script; or ``{"error": str}``.
        """
        try:
            safe = "".join(ch for ch in name if ch.isalnum() or ch in ("_", "-"))
            filename = f"{safe}.py" if not safe.endswith(".py") else safe
            p = _ensure_within_workspace(workspace, scripts_dir / filename)
        except Exception:
            return {"error": "Invalid path"}
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {"script": str(p.relative_to(workspace))}
        except Exception as e:
            return {"error": str(e)}

    @app.tool
    async def run_script(ctx: Context, path: str, args: list[str] | None = None, timeout: int = 120) -> dict:  # noqa: ARG001
        """Run a Python script in a subprocess and report artifacts.

        Args:
          ctx: FastMCP request context (unused).
          path: Relative script path under the workspace.
          args: Optional command-line arguments passed to the script.
          timeout: Seconds before the subprocess is terminated.

        Returns:
          ``{"stdout": str, "stderr": str, "returncode": int, "new_files": list[str]}``;
          or ``{"error": str}`` on failure.
        """
        try:
            script_path = _ensure_within_workspace(workspace, Path(path))
        except Exception:
            return {"error": "Invalid path"}
        if not script_path.exists():
            return {"error": "Script not found"}
        if args is None:
            args = []
        before = snapshot_workspace_files()
        try:
            proc = subprocess.run(
                [os.environ.get("PYTHON", "python"), str(script_path)] + list(args),
                cwd=str(workspace),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = proc.stdout
            stderr = proc.stderr
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            return {"error": "Timeout"}
        after = snapshot_workspace_files()
        new_files = sorted(list(after - before))
        return {"stdout": stdout, "stderr": stderr, "returncode": rc, "new_files": new_files}

    @app.tool
    async def install_dependencies(ctx: Context, packages: list[str]) -> dict:  # noqa: ARG001
        """Install Python packages into the current environment.

        Prefers ``uv pip install`` when available; otherwise falls back to
        ``python -m pip install``.

        Args:
          ctx: FastMCP request context (unused).
          packages: List of package specifiers.

        Returns:
          ``{"returncode": int, "stdout": str, "stderr": str}`` from the installer.
        """
        if not packages:
            return {"error": "No packages provided"}
        cmds = []
        if shutil.which("uv"):
            cmds.append(["uv", "pip", "install", *packages])
        cmds.append([os.environ.get("PYTHON", "python"), "-m", "pip", "install", "--disable-pip-version-check", *packages])
        last = {"returncode": -1, "stdout": "", "stderr": ""}
        for cmd in cmds:
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True)
                last = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
                if proc.returncode == 0:
                    return last
            except Exception as e:
                last = {"returncode": -1, "stdout": "", "stderr": str(e)}
        return last

    @app.tool
    async def list_variables(ctx: Context) -> dict:  # noqa: ARG001
        """List non-private variable names in the kernel's globals.

        Args:
          ctx: FastMCP request context (unused).

        Returns:
          ``{"variables": list[str]}`` of best-effort global names (modules filtered).
        """
        client = kernel_manager.get_client()
        code = (
            "import builtins,types\n"
            "_vars=[k for k,v in globals().items() if not k.startswith('_') and not isinstance(v, types.ModuleType)]\n"
            "print('\n'.join(sorted(_vars)))\n"
        )
        msg_id = client.execute(code)
        names: list[str] = []
        while True:
            try:
                msg = client.get_iopub_msg(timeout=1)
                if msg['parent_header']['msg_id'] != msg_id:
                    continue
                if msg['header']['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                    break
                if msg['header']['msg_type'] == 'stream' and msg['content']['name'] == 'stdout':
                    stdout_text = msg['content']['text']
                    names.extend([line for line in stdout_text.splitlines() if line.strip()])
            except asyncio.TimeoutError:
                break
            except Exception:
                break
        return {"variables": sorted(set(names))}

    @app.tool
    async def restart_kernel(ctx: Context) -> dict:  # noqa: ARG001
        """Restart the Jupyter kernel and clear its state.

        Args:
          ctx: FastMCP request context (unused).

        Returns:
          ``{"restarted": True}`` on success; or ``{"error": str}``.
        """
        try:
            kernel_manager.shutdown_kernel()
            type(kernel_manager)._km = KernelManager()
            type(kernel_manager)._km.start_kernel()
            type(kernel_manager)._client = type(kernel_manager)._km.client()
            type(kernel_manager)._client.start_channels()
            return {"restarted": True}
        except Exception as e:
            return {"error": str(e)}

    @app.tool
    async def get_workspace_info(ctx: Context) -> dict:  # noqa: ARG001
        """Return absolute paths for the active workspace layout.

        Args:
          ctx: FastMCP request context (unused).

        Returns:
          ``{"workspace": str, "scripts": str, "outputs": str, "uploads": str}``.
        """
        return {
            "workspace": str(workspace),
            "scripts": str(scripts_dir),
            "outputs": str(outputs_dir),
            "uploads": str(uploads_dir),
        }

    @app.custom_route("/files/upload", methods=["POST"])
    async def upload_file(request: Request):  # type: ignore[unused-ignore]
        """Upload a file into ``uploads/`` under the workspace via multipart/form-data.

        Form field: ``file``.
        """
        form = await request.form()
        upload_file = form["file"]
        raw_name = Path(upload_file.filename).name
        try:
            filepath = _ensure_within_workspace(workspace, uploads_dir / raw_name)
        except Exception:
            return JSONResponse({"error": "Invalid path"}, status_code=400)
        with open(filepath, "wb") as f:
            f.write(await upload_file.read())
        return JSONResponse({"filename": filepath.name})

    @app.custom_route("/files/download/{path:path}", methods=["GET"])
    async def download_file(request: Request):  # type: ignore[unused-ignore]
        """Serve a file from the workspace by relative path.

        Example: ``GET /files/download/uploads/name.txt``.
        """
        path = request.path_params['path']
        try:
            filepath = _ensure_within_workspace(workspace, Path(path))
        except Exception:
            return JSONResponse({"error": "Invalid path"}, status_code=400)
        if not filepath.exists():
            return JSONResponse({"error": "File not found"}, status_code=404)
        return FileResponse(filepath)

    # Attach some convenience attributes for running via entry points
    app._host = "127.0.0.1"  # type: ignore[attr-defined]
    app._port = 8000  # type: ignore[attr-defined]
    app._workspace = str(workspace)  # type: ignore[attr-defined]
    return app


def run_http(host: str = "127.0.0.1", port: int = 8000, workspace: Optional[str] = None) -> None:
    """Run the FastMCP server over HTTP.

    Args:
      host: Bind host (default ``127.0.0.1``).
      port: Bind port (default ``8000``).
      workspace: Optional workspace directory path; if provided, sets
        ``MCP_WORKSPACE_DIR`` for the process before app creation.
    """
    if workspace:
        os.environ["MCP_WORKSPACE_DIR"] = workspace
    app = create_app()
    app.run(transport="http", host=host, port=port)
