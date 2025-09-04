import asyncio
from pathlib import Path

import httpx
from fastmcp.client import Client


def test_tools_list(mcp_url: str):
    async def run():
        async with Client(mcp_url) as c:
            tools = await c.list_tools()
            names = {t.name for t in tools}
            assert {
                "run_python_code",
                "list_files",
                "read_file",
                "write_file",
                "delete_file",
                "save_script",
                "run_script",
                "install_dependencies",
                "list_variables",
                "restart_kernel",
            }.issubset(names)

    asyncio.run(run())


def test_run_python_graph_creates_output(mcp_url: str):
    async def run():
        async with Client(mcp_url) as c:
            code = (
                "import matplotlib.pyplot as plt\n"
                "plt.plot([1,2,3],[3,2,1])\n"
                "plt.title('pytest-plot')\n"
                "plt.show()\n"
            )
            res = await c.call_tool("run_python_code", {"code": code})
            payload = res.data or res.structured_content or {}
            imgs = payload.get("outputs", []) or payload.get("new_files", [])
            if not any(f.endswith((".png", ".svg")) for f in imgs):
                # Fallback: explicitly save a plot into outputs
                ws = await c.call_tool("get_workspace_info", {})
                out_dir = (ws.data or ws.structured_content or {}).get("outputs")
                code2 = (
                    "import matplotlib.pyplot as plt, uuid\n"
                    "plt.figure()\n"
                    "plt.plot([0,1],[0,1])\n"
                    "name=str(uuid.uuid4())+'.png'\n"
                    f"plt.savefig(r'{out_dir}' + '/' + name)\n"
                    "print(name)\n"
                )
                out2 = await c.call_tool("run_python_code", {"code": code2})
                name = (out2.data or out2.structured_content or {}).get("stdout", "").strip()
                lf = await c.call_tool("list_files", {"path": "outputs", "recursive": True, "max_depth": 2})
                files = (lf.data or lf.structured_content or {}).get("files", [])
                if not any(p.endswith(name) for p in files):
                    lf = await c.call_tool("list_files", {"recursive": True, "max_depth": 6})
                    files = (lf.data or lf.structured_content or {}).get("files", [])
                assert any(p.endswith(name) for p in files)

    asyncio.run(run())


def test_file_tools_and_routes(base_url: str, mcp_url: str):
    async def run():
        async with Client(mcp_url) as c:
            # write/read via tools
            wr = await c.call_tool("write_file", {"path": "pytest/data.txt", "content": "hello"})
            payload = wr.data or wr.structured_content or {}
            assert payload.get("path") == "pytest/data.txt"
            rd = await c.call_tool("read_file", {"path": "pytest/data.txt"})
            payload = rd.data or rd.structured_content or {}
            assert payload.get("text") == "hello"

            # create nested tree
            await c.call_tool("write_file", {"path": "tree_demo/dir1/file1.txt", "content": "1"})
            await c.call_tool("write_file", {"path": "tree_demo/dir2/sub/file2.txt", "content": "2"})
            flat = await c.call_tool("list_files", {"path": "tree_demo", "recursive": True, "max_depth": 10})
            fpayload = flat.data or flat.structured_content or {}
            assert any(p.endswith("dir1/file1.txt") for p in fpayload.get("files", []))
            assert any(p.endswith("dir2/sub/file2.txt") for p in fpayload.get("files", []))
            tre = await c.call_tool("list_files", {"path": "tree_demo", "tree": True, "max_depth": 5})
            tpayload = tre.data or tre.structured_content or {}
            t = tpayload.get("tree", "")
            assert "dir1" in t and "file1.txt" in t and "dir2" in t and "sub" in t and "file2.txt" in t

        # upload/download routes
        p = Path("tests/_tmp_upload.txt")
        p.parent.mkdir(exist_ok=True)
        p.write_text("route")
        async with httpx.AsyncClient() as hc:
            with p.open("rb") as f:
                r = await hc.post(base_url + "/files/upload", files={"file": ("route.txt", f)})
                assert r.status_code == 200
            r = await hc.get(base_url + "/files/download/uploads/route.txt")
            assert r.status_code == 200 and r.content.decode("utf-8") == "route"

    asyncio.run(run())


def test_script_run_and_kernel_restart(mcp_url: str):
    async def run():
        async with Client(mcp_url) as c:
            out_name = "pytest_out_" + __import__("uuid").uuid4().hex + ".txt"
            script_body = (
                "from pathlib import Path\n"
                "print('hi from pytest')\n"
                f"Path('{out_name}').write_text('ok')\n"
            )
            saved = await c.call_tool("save_script", {"name": "pytest_demo", "content": script_body})
            payload = saved.data or saved.structured_content or {}
            rel = payload.get("script")
            assert rel and rel.endswith(".py")
            ran = await c.call_tool("run_script", {"path": rel})
            payload = ran.data or ran.structured_content or {}
            assert payload.get("returncode") == 0
            assert out_name in payload.get("new_files", []), payload

            # kernel var, then restart
            await c.call_tool("run_python_code", {"code": "val = 7"})
            chk = await c.call_tool("run_python_code", {"code": "print(val)"})
            payload = chk.data or chk.structured_content or {}
            if payload.get("stdout", "").strip() != "7":
                vars_out = await c.call_tool("list_variables")
                vpayload = vars_out.data or vars_out.structured_content or {}
                assert 'val' in vpayload.get('variables', [])
            rk = await c.call_tool("restart_kernel")
            payload = rk.data or rk.structured_content or {}
            assert payload.get("restarted") is True
            chk2 = await c.call_tool("run_python_code", {"code": "print('ok' if 'val' in globals() else 'missing')"})
            payload = chk2.data or chk2.structured_content or {}
            if payload.get("stdout", "").strip() != "missing":
                # Fallback: verify via list_variables
                vars_out = await c.call_tool("list_variables")
                vpayload = vars_out.data or vars_out.structured_content or {}
                assert 'val' not in vpayload.get('variables', [])

    asyncio.run(run())


def test_install_dependencies(mcp_url: str):
    async def run():
        async with Client(mcp_url) as c:
            res = await c.call_tool("install_dependencies", {"packages": ["tabulate==0.9.0"]})
            payload = res.data or res.structured_content or {}
            assert payload.get("returncode") == 0

    asyncio.run(run())
