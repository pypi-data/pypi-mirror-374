# Python Interpreter MCP

A FastMCP-based Model Context Protocol (MCP) server focused on data analysis. It provides a persistent Jupyter kernel to execute Python code, manage files, run scripts, capture rich outputs (plots, SVG, JSON), and install Python dependencies.

## Features
- Stateful Jupyter kernel (`run_python_code`) with stdout/stderr capture
- Auto-saves rich display outputs to `outputs/` and returns file paths
- Workspace-scoped file tools: list, tree view, read, write, delete
- Script lifecycle: save under `scripts/`, run via subprocess, track new artifacts
- Dependency installer using `uv pip` or `pip`
- Configurable workspace directory via CLI or env
- HTTP routes for upload/download

## Requirements
- Python 3.12+
- uv (recommended): https://docs.astral.sh/uv/

Install dependencies:
- uv sync

## Running
- Default workspace (`./workspace`):
  - uv run python main.py
- Custom workspace:
  - uv run python main.py --workspace /abs/path/to/work
  - or set env: MCP_WORKSPACE_DIR=/abs/path/to/work uv run python main.py
- Endpoint: http://127.0.0.1:8000/mcp

## Workspace Layout
- `workspace/`
  - `scripts/`: scripts saved by `save_script`
  - `outputs/`: rich display outputs (png/svg/json) saved by `run_python_code`
  - `uploads/`: files received by the upload route
  - your data files

## Tools (MCP)
- `run_python_code(code: str)` → stdout, stderr, results, outputs, new_files
- `code_completion(code: str, cursor_pos: int)` → Jupyter completion reply
- `inspect_object(code: str, cursor_pos: int, detail_level: int)` → inspection reply
- `list_files(path?: str, recursive?: bool, tree?: bool, max_depth?: int, include_files?: bool, include_dirs?: bool)` → flat listing or ASCII tree
- `read_file(path: str, max_bytes?: int)` → {text} or {base64}
- `write_file(path: str, content: str, binary_base64?: bool)` → {path}
- `delete_file(filename: str)` → {success}
- `save_script(name: str, content: str)` → {script}
- `run_script(path: str, args?: list[str], timeout?: int)` → stdout, stderr, returncode, new_files
- `install_dependencies(packages: list[str])` → returncode, stdout, stderr
- `list_variables()` → {variables}
- `restart_kernel()` → {restarted}
- `get_workspace_info()` → {workspace, scripts, outputs, uploads}
- `ping()` → {ok}

## HTTP Routes
- Upload: `POST /files/upload` (multipart field `file`) → {filename}
  - Saved to `uploads/{filename}`
- Download: `GET /files/download/{path}` for nested paths
  - Example: `/files/download/outputs/abc.png`

## Examples
- Plot and return a file path:
  - `run_python_code`: `import matplotlib.pyplot as plt; plt.plot([1,2]); plt.show()`
  - Response includes `outputs: ["outputs/<uuid>.png"]` and `new_files` with the same path
- Save + run script:
  - `save_script` → `scripts/demo.py`
  - `run_script` → returns `stdout/stderr` and `new_files` (e.g., generated CSVs)
- List a tree (ASCII):
  - `list_files` with `{"path": "data", "tree": true, "max_depth": 3}`

## Development
- Run tests: `uv run pytest -q`
- Lint/format: not enforced; follow PEP 8
- Add a new tool: decorate with `@mcp.tool`, return JSON-serializable data, and keep file access within `WORKSPACE_DIR`

## Security Notes
- All file operations are restricted to the configured workspace (path checks resolve symlinks)
- Use a dedicated workspace for untrusted data
- Consider containerizing for added isolation

## Clients
This server uses Streamable HTTP transport and should work with clients that support HTTP MCP. Example clients: Claude Desktop (custom connectors), MCP Inspector, fastmcp.client.

