import os
from pathlib import Path
import importlib


def test_path_safety_helper(tmp_path: Path):
    os.environ["MCP_WORKSPACE_DIR"] = str(tmp_path)
    app_mod = importlib.import_module("python_mcp_server.app")
    # in workspace ok
    p = app_mod._ensure_within_workspace(Path(tmp_path), Path("ok.txt"))
    assert Path(p).parent == tmp_path
    # escape blocked
    import pytest
    with pytest.raises(Exception):
        app_mod._ensure_within_workspace(Path(tmp_path), Path("../escape.txt"))


def test_render_tree_helper(tmp_path: Path):
    os.environ["MCP_WORKSPACE_DIR"] = str(tmp_path)
    app_mod = importlib.import_module("python_mcp_server.app")
    # populate
    (tmp_path / "d1").mkdir()
    (tmp_path / "d1" / "f1.txt").write_text("1")
    (tmp_path / "d2" / "sub").mkdir(parents=True)
    (tmp_path / "d2" / "sub" / "f2.txt").write_text("2")

    txt = app_mod._render_tree(tmp_path, max_depth=5, include_files=True, include_dirs=True)
    assert "d1" in txt and "f1.txt" in txt and "d2" in txt and "sub" in txt and "f2.txt" in txt


def test_snapshot_workspace_files_helper(tmp_path: Path):
    os.environ["MCP_WORKSPACE_DIR"] = str(tmp_path)
    app_mod = importlib.import_module("python_mcp_server.app")
    _ = app_mod.create_app()
    before = {str(p.relative_to(tmp_path)) for p in tmp_path.rglob('*') if p.is_file()}
    (tmp_path / "x.txt").write_text("x")
    after = {str(p.relative_to(tmp_path)) for p in tmp_path.rglob('*') if p.is_file()}
    assert "x.txt" in (after - before)


def test_workspace_dirs_created(tmp_path: Path):
    os.environ["MCP_WORKSPACE_DIR"] = str(tmp_path)
    app_mod = importlib.import_module("python_mcp_server.app")
    _ = app_mod.create_app()
    assert (tmp_path / "scripts").exists()
    assert (tmp_path / "outputs").exists()
    assert (tmp_path / "uploads").exists()
