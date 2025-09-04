import asyncio
import base64
import atexit
import uuid
import os
import json
import shutil
import subprocess
from pathlib import Path
import argparse

from jupyter_client.manager import KernelManager
from starlette.responses import FileResponse, JSONResponse
from starlette.requests import Request

from fastmcp import FastMCP, Context

# --- Kernel Manager Singleton ---

class KernelManagerSingleton:
    _instance = None
    _km = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KernelManagerSingleton, cls).__new__(cls)
            cls._km = KernelManager()
            cls._km.start_kernel()
            print("Jupyter Kernel Started")
            cls._client = cls._km.client()
            cls._client.start_channels()
            
            # Ensure the kernel is shut down when the application exits
            atexit.register(cls._instance.shutdown_kernel)
        return cls._instance

    def get_client(self):
        return self._client

    def shutdown_kernel(self):
        if self._km and self._km.is_alive():
            print("Shutting down Jupyter Kernel...")
            self._km.shutdown_kernel(now=True)
            print("Jupyter Kernel Shutdown")

# Initialize the singleton
kernel_manager = KernelManagerSingleton()

# --- Workspace Setup ---
MCP_WORKSPACE_ENV = os.environ.get("MCP_WORKSPACE_DIR", "workspace")
WORKSPACE_DIR = Path(MCP_WORKSPACE_ENV).resolve()
SCRIPTS_DIR = WORKSPACE_DIR / "scripts"
OUTPUTS_DIR = WORKSPACE_DIR / "outputs"
UPLOADS_DIR = WORKSPACE_DIR / "uploads"
for d in (WORKSPACE_DIR, SCRIPTS_DIR, OUTPUTS_DIR, UPLOADS_DIR):
    d.mkdir(parents=True, exist_ok=True)

def _ensure_within_workspace(p: Path) -> Path:
    p = (WORKSPACE_DIR / p).resolve() if not p.is_absolute() else p.resolve()
    if WORKSPACE_DIR not in p.parents and p != WORKSPACE_DIR:
        raise ValueError("Path escapes workspace")
    return p

# --- FastMCP Server ---

mcp = FastMCP(name="Python Interpreter MCP")

def _snapshot_workspace_files() -> set[str]:
    return {
        str(p.relative_to(WORKSPACE_DIR))
        for p in WORKSPACE_DIR.rglob("*")
        if p.is_file()
    }


@mcp.tool
async def run_python_code(ctx: Context, code: str) -> dict:
    """Execute Python code in the persistent Jupyter kernel.

    The kernel session is shared across calls, enabling stateful workflows.
    Rich display outputs (image/png, image/svg+xml, application/json) are saved
    under `outputs/` and their relative paths are returned.

    Args:
        ctx: FastMCP request context.
        code: Python source to execute.

    Returns:
        dict: A payload containing:
            stdout: Captured standard output.
            stderr: Captured standard error and tracebacks.
            results: Text/plain execute_result payloads.
            outputs: Relative paths to saved display outputs under outputs/.
            new_files: Relative paths of files newly created under the workspace.
    """
    client = kernel_manager.get_client()
    
    # Clear any pending messages
    while True:
        try:
            client.get_shell_msg(timeout=0.1)
        except Exception:
            break

    # Snapshot files before execution to detect newly created outputs
    before_files = _snapshot_workspace_files()

    msg_id = client.execute(code)
    
    stdout = ""
    stderr = ""
    outputs = []
    results = []

    while True:
        try:
            msg = client.get_iopub_msg(timeout=1)
            if msg['parent_header']['msg_id'] != msg_id:
                continue

            msg_type = msg['header']['msg_type']

            if msg_type == 'status':
                if msg['content']['execution_state'] == 'idle':
                    break
            
            elif msg_type == 'stream':
                if msg['content']['name'] == 'stdout':
                    stdout += msg['content']['text']
                else:
                    stderr += msg['content']['text']

            elif msg_type in ('display_data', 'execute_result'):
                data = msg['content']['data']
                # Save images
                if 'image/png' in data:
                    img_data = base64.b64decode(data['image/png'])
                    filename = f"{uuid.uuid4()}.png"
                    filepath = OUTPUTS_DIR / filename
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    outputs.append(str(filepath.relative_to(WORKSPACE_DIR)))
                # Save SVG if provided
                elif 'image/svg+xml' in data:
                    svg_text = data['image/svg+xml']
                    filename = f"{uuid.uuid4()}.svg"
                    filepath = OUTPUTS_DIR / filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(svg_text)
                    outputs.append(str(filepath.relative_to(WORKSPACE_DIR)))
                # Save JSON payloads to a file for later retrieval
                if 'application/json' in data:
                    try:
                        parsed = data['application/json']
                        filename = f"{uuid.uuid4()}.json"
                        filepath = OUTPUTS_DIR / filename
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(parsed, f)
                        outputs.append(str(filepath.relative_to(WORKSPACE_DIR)))
                    except Exception:
                        pass
                # Capture plain text results too
                if 'text/plain' in data:
                    results.append(str(data['text/plain']))
            
            elif msg_type == 'error':
                stderr += "\n".join(msg['content']['traceback'])

        except asyncio.TimeoutError:
            # Kernel is idle
            break
        except Exception as e:
            # Something went wrong with message handling
            stderr += f"Error processing kernel message: {e}"
            break

    # Detect any files created during execution
    after_files = _snapshot_workspace_files()
    new_files = sorted(list(after_files - before_files))

    return {
        "stdout": stdout,
        "stderr": stderr,
        "results": results,
        "outputs": outputs,
        "new_files": new_files,
    }

@mcp.tool
async def code_completion(ctx: Context, code: str, cursor_pos: int) -> dict:
    """Provide code completion suggestions from the Jupyter kernel.

    Args:
        ctx: FastMCP request context.
        code: Buffer contents to complete against.
        cursor_pos: Cursor index within `code` to request completions for.

    Returns:
        dict: Raw Jupyter completion reply.
    """
    client = kernel_manager.get_client()
    client.complete(code, cursor_pos)
    msg = client.get_shell_msg(timeout=1)
    return msg['content']

@mcp.tool
async def inspect_object(ctx: Context, code: str, cursor_pos: int, detail_level: int = 0) -> dict:
    """Inspect an object/expression within the kernel namespace.

    Args:
        ctx: FastMCP request context.
        code: Buffer containing the target expression.
        cursor_pos: Cursor index within `code` to inspect.
        detail_level: Jupyter detail level (0 minimal, higher is more verbose).

    Returns:
        dict: Raw Jupyter inspection reply.
    """
    client = kernel_manager.get_client()
    client.inspect(code, cursor_pos, detail_level)
    msg = client.get_shell_msg(timeout=1)
    return msg['content']

def _render_tree(root: Path, max_depth: int | None = 3, include_files: bool = True, include_dirs: bool = True) -> str:
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


@mcp.tool
async def list_files(
    ctx: Context,
    path: str | None = None,
    recursive: bool = False,
    tree: bool = False,
    max_depth: int | None = 3,
    include_files: bool = True,
    include_dirs: bool = True,
) -> dict:
    """List workspace files/directories with flat or tree output.

    Args:
        ctx: FastMCP request context.
        path: Optional relative subpath. Defaults to workspace root.
        recursive: If True, return all descendants (flat list in `files`).
        tree: If True, return an ASCII tree rendering in `tree`.
        max_depth: Depth cap for recursion/tree; None for unlimited.
        include_files: Include files in results.
        include_dirs: Include directories in results.

    Returns:
        dict: Flat listing -> {root, files}; tree -> {root, tree}. On error -> {error}.
    """
    try:
        base = _ensure_within_workspace(WORKSPACE_DIR / (path or ""))
    except Exception:
        return {"error": "Invalid path"}

    if tree:
        root = base
        if not root.exists():
            return {"error": "Path not found"}
        if root.is_file():
            # Tree for a file is trivial
            rel = root.relative_to(WORKSPACE_DIR)
            return {"root": str(rel), "tree": rel.name}
        txt = _render_tree(root, max_depth=max_depth, include_files=include_files, include_dirs=include_dirs)
        return {"root": str(base.relative_to(WORKSPACE_DIR)), "tree": txt}

    # Flat listing
    if not base.exists():
        return {"error": "Path not found"}

    if recursive:
        results: list[str] = []
        for p in base.rglob("*"):
            if not ((include_files and p.is_file()) or (include_dirs and p.is_dir())):
                continue
            # Respect max_depth if provided
            if max_depth is not None:
                try:
                    depth = len(p.relative_to(base).parts)
                except Exception:
                    depth = 0
                if depth > max_depth:
                    continue
            results.append(str(p.relative_to(WORKSPACE_DIR)))
        return {"root": str(base.relative_to(WORKSPACE_DIR)) if base != WORKSPACE_DIR else ".", "files": sorted(results)}
    else:
        try:
            entries = [
                str((base / c.name).relative_to(WORKSPACE_DIR))
                for c in base.iterdir()
                if (include_files and c.is_file()) or (include_dirs and c.is_dir())
            ]
        except Exception as e:
            return {"error": str(e)}
        return {"root": str(base.relative_to(WORKSPACE_DIR)) if base != WORKSPACE_DIR else ".", "files": sorted(entries)}

@mcp.tool
async def ping(ctx: Context) -> dict:
    """Health check for the MCP server.

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {ok: True}
    """
    return {"ok": True}

@mcp.tool
async def delete_file(ctx: Context, filename: str) -> dict:
    """Delete a file from the workspace.

    Args:
        ctx: FastMCP request context.
        filename: Relative path of the file to delete.

    Returns:
        dict: {success: True} on success; otherwise {error} with status code.
    """
    try:
        filepath = _ensure_within_workspace(Path(filename))
    except Exception:
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    if not filepath.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    try:
        os.remove(filepath)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@mcp.tool
async def read_file(ctx: Context, path: str, max_bytes: int | None = None) -> dict:
    """Read a text or binary file from the workspace.

    Attempts UTF-8 decoding; if that fails, returns base64-encoded bytes.

    Args:
        ctx: FastMCP request context.
        path: Relative file path.
        max_bytes: Optional byte limit to truncate content.

    Returns:
        dict: {text} for UTF-8, or {base64} for binary; or {error}.
    """
    try:
        filepath = _ensure_within_workspace(Path(path))
        if not filepath.exists() or not filepath.is_file():
            return {"error": "File not found"}
        data = filepath.read_bytes()
        if max_bytes is not None:
            data = data[:max_bytes]
        try:
            return {"text": data.decode("utf-8")}
        except UnicodeDecodeError:
            return {"base64": base64.b64encode(data).decode("ascii")}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def write_file(ctx: Context, path: str, content: str, binary_base64: bool = False) -> dict:
    """Write a file under the workspace (text or base64-encoded binary).

    Args:
        ctx: FastMCP request context.
        path: Relative destination path.
        content: Text or base64 data.
        binary_base64: Treat `content` as base64 and write bytes when True.

    Returns:
        dict: {path} relative to the workspace; or {error}.
    """
    try:
        filepath = _ensure_within_workspace(Path(path))
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if binary_base64:
            data = base64.b64decode(content)
            filepath.write_bytes(data)
        else:
            filepath.write_text(content, encoding="utf-8")
        return {"path": str(filepath.relative_to(WORKSPACE_DIR))}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def save_script(ctx: Context, name: str, content: str) -> dict:
    """Save a Python script under `scripts/`.

    Args:
        ctx: FastMCP request context.
        name: Script filename; `.py` appended if missing.
        content: Python source code.

    Returns:
        dict: {script} relative path under the workspace; or {error}.
    """
    if not name.endswith(".py"):
        name = f"{name}.py"
    try:
        target = _ensure_within_workspace(SCRIPTS_DIR / name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"script": str(target.relative_to(WORKSPACE_DIR))}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def run_script(ctx: Context, path: str, args: list[str] | None = None, timeout: int = 120) -> dict:
    """Run a Python script in a subprocess and report artifacts.

    Args:
        ctx: FastMCP request context.
        path: Relative script path under the workspace.
        args: Optional subprocess arguments.
        timeout: Seconds until execution times out.

    Returns:
        dict: {stdout, stderr, returncode, new_files}; or {error}.
    """
    try:
        script_path = _ensure_within_workspace(Path(path))
    except Exception:
        return {"error": "Invalid path"}
    if not script_path.exists():
        return {"error": "Script not found"}
    if args is None:
        args = []
    before = _snapshot_workspace_files()
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"), str(script_path)] + list(args),
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        return {"error": "Timeout"}
    after = _snapshot_workspace_files()
    new_files = sorted(list(after - before))
    return {"stdout": stdout, "stderr": stderr, "returncode": rc, "new_files": new_files}

@mcp.tool
async def install_dependencies(ctx: Context, packages: list[str]) -> dict:
    """Install Python packages into the current environment.

    Prefers `uv pip install` when available; otherwise uses `python -m pip install`.

    Args:
        ctx: FastMCP request context.
        packages: List of package specifiers.

    Returns:
        dict: {returncode, stdout, stderr} from the installer.
    """
    if not packages:
        return {"error": "No packages provided"}
    cmds = []
    # Prefer uv if available (works well in uv-managed envs)
    if shutil.which("uv"):
        cmds.append(["uv", "pip", "install", *packages])
    # Fallback to pip if present
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

@mcp.tool
async def list_variables(ctx: Context) -> dict:
    """List variable names in the kernel's global namespace (best-effort).

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {variables: list[str]} of non-private globals (modules filtered).
    """
    client = kernel_manager.get_client()
    code = (
        "import builtins,types\n"
        "_vars=[k for k,v in globals().items() if not k.startswith('_') and not isinstance(v, types.ModuleType)]\n"
        "print('\n'.join(sorted(_vars)))\n"
    )
    msg_id = client.execute(code)
    names = []
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

@mcp.tool
async def restart_kernel(ctx: Context) -> dict:
    """Restart the Jupyter kernel and clear state.

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {restarted: True} on success; or {error}.
    """
    try:
        kernel_manager.shutdown_kernel()
        # Recreate singleton internals
        type(kernel_manager)._km = KernelManager()
        type(kernel_manager)._km.start_kernel()
        type(kernel_manager)._client = type(kernel_manager)._km.client()
        type(kernel_manager)._client.start_channels()
        return {"restarted": True}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def get_workspace_info(ctx: Context) -> dict:
    """Return absolute paths for the active workspace layout.

    Args:
        ctx: FastMCP request context.

    Returns:
        dict: {workspace, scripts, outputs, uploads} absolute paths.
    """
    return {
        "workspace": str(WORKSPACE_DIR),
        "scripts": str(SCRIPTS_DIR),
        "outputs": str(OUTPUTS_DIR),
        "uploads": str(UPLOADS_DIR),
    }

@mcp.custom_route("/files/upload", methods=["POST"])
async def upload_file(request: Request):
    """Handles file uploads."""
    form = await request.form()
    upload_file = form["file"]
    raw_name = Path(upload_file.filename).name
    try:
        filepath = _ensure_within_workspace(UPLOADS_DIR / raw_name)
    except Exception:
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    with open(filepath, "wb") as f:
        f.write(await upload_file.read())
    return JSONResponse({"filename": filepath.name})

@mcp.custom_route("/files/download/{path:path}", methods=["GET"])
async def download_file(request: Request):
    """Serves a file from the workspace directory."""
    path = request.path_params['path']
    try:
        filepath = _ensure_within_workspace(Path(path))
    except Exception:
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    if not filepath.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(filepath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python Interpreter MCP")
    parser.add_argument("--workspace", type=str, default=os.environ.get("MCP_WORKSPACE_DIR", "workspace"), help="Workspace directory for files, scripts, outputs")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Recompute directories if overridden via CLI
    ws = Path(args.workspace).resolve()
    if ws != WORKSPACE_DIR:
        globals()["WORKSPACE_DIR"] = ws
        globals()["SCRIPTS_DIR"] = (ws / "scripts").resolve()
        globals()["OUTPUTS_DIR"] = (ws / "outputs").resolve()
        globals()["UPLOADS_DIR"] = (ws / "uploads").resolve()
        for d in (WORKSPACE_DIR, SCRIPTS_DIR, OUTPUTS_DIR, UPLOADS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    mcp.run(transport="http", host=args.host, port=args.port)
