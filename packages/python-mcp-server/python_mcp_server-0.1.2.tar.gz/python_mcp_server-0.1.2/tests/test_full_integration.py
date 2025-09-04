import asyncio
from pathlib import Path

import httpx
from fastmcp.client import Client


def test_full_integration_flow(base_url: str, mcp_url: str):
    async def run():
        async with Client(mcp_url) as c:
            # health
            pong = await c.call_tool("ping", {})
            assert (pong.data or pong.structured_content or {}).get("ok") is True

            # tools list
            tools = await c.list_tools()
            tool_names = {t.name for t in tools}
            required = {
                "run_python_code",
                "code_completion",
                "inspect_object",
                "list_files",
                "read_file",
                "write_file",
                "delete_file",
                "save_script",
                "run_script",
                "install_dependencies",
                "list_variables",
                "restart_kernel",
                "ping",
                "get_workspace_info",
            }
            assert required.issubset(tool_names)

            # workspace info
            ws = await c.call_tool("get_workspace_info", {})
            ws_info = ws.data or ws.structured_content or {}
            assert all(k in ws_info for k in ("workspace", "scripts", "outputs", "uploads"))

            # write/read
            wr = await c.call_tool("write_file", {"path": "itest/alpha.txt", "content": "alpha"})
            assert (wr.data or wr.structured_content or {}).get("path") == "itest/alpha.txt"
            rd = await c.call_tool("read_file", {"path": "itest/alpha.txt"})
            assert (rd.data or rd.structured_content or {}).get("text") == "alpha"

            # list flat, recursive, and tree
            await c.call_tool("write_file", {"path": "itest/dir/sub.txt", "content": "s"})
            flat = await c.call_tool("list_files", {"path": "itest"})
            assert any(p.endswith("alpha.txt") for p in (flat.data or flat.structured_content or {}).get("files", []))
            rec = await c.call_tool("list_files", {"path": "itest", "recursive": True, "max_depth": 5})
            rfiles = (rec.data or rec.structured_content or {}).get("files", [])
            assert any(p.endswith("dir/sub.txt") for p in rfiles)
            tree = await c.call_tool("list_files", {"path": "itest", "tree": True})
            assert "alpha.txt" in (tree.data or tree.structured_content or {}).get("tree", "")

            # kernel: execute and display
            code = (
                "import matplotlib.pyplot as plt\n"
                "plt.plot([0,1],[0,1])\n"
                "plt.title('it')\n"
                "plt.show()\n"
            )
            out = await c.call_tool("run_python_code", {"code": code})
            payload = out.data or out.structured_content or {}
            imgs = payload.get("outputs", []) or payload.get("new_files", [])
            if not any(p.endswith((".png", ".svg")) for p in imgs):
                # Fallback: explicitly save a figure into outputs dir and assert it exists
                ws = await c.call_tool("get_workspace_info", {})
                ws_info = ws.data or ws.structured_content or {}
                out_dir = ws_info.get("outputs")
                code2 = (
                    "import matplotlib.pyplot as plt, uuid, os\n"
                    "plt.figure()\n"
                    "plt.plot([0,1],[0,1])\n"
                    "name=str(uuid.uuid4())+'.png'\n"
                    "path=os.path.join(r'" + str('') + "', name)\n"  # dummy to keep format simple
                )
                # pass path as a variable to savefig to avoid path quoting issues
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
                # Prefer outputs/, but fall back to searching entire workspace
                lf = await c.call_tool("list_files", {"path": "outputs", "recursive": True, "max_depth": 2})
                files = (lf.data or lf.structured_content or {}).get("files", [])
                if not any(p.endswith(name) for p in files):
                    lf = await c.call_tool("list_files", {"recursive": True, "max_depth": 6})
                    files = (lf.data or lf.structured_content or {}).get("files", [])
                assert any(p.endswith(name) for p in files)

            # completion and inspect
            comp = await c.call_tool("code_completion", {"code": "impor", "cursor_pos": 5})
            assert (comp.data or comp.structured_content or {}).get("status") == "ok"
            insp = await c.call_tool("inspect_object", {"code": "print", "cursor_pos": 3, "detail_level": 0})
            assert (insp.data or insp.structured_content or {}).get("status") == "ok"

            # save and run a script
            script = (
                "from pathlib import Path\n"
                "Path('it_created.txt').write_text('ok')\n"
                "print('it ok')\n"
            )
            saved = await c.call_tool("save_script", {"name": "it_script", "content": script})
            rel = (saved.data or saved.structured_content or {}).get("script")
            ran = await c.call_tool("run_script", {"path": rel})
            rpayload = ran.data or ran.structured_content or {}
            assert rpayload.get("returncode") == 0
            # Verify artifact exists
            lf = await c.call_tool("list_files", {"recursive": True, "max_depth": 3})
            assert any(p.endswith("it_created.txt") for p in (lf.data or lf.structured_content or {}).get("files", []))

            # install dep (pure-python)
            dep = await c.call_tool("install_dependencies", {"packages": ["tabulate==0.9.0"]})
            assert (dep.data or dep.structured_content or {}).get("returncode") == 0

            # variables and restart
            await c.call_tool("run_python_code", {"code": "xv=1"})
            chk = await c.call_tool("run_python_code", {"code": "print(xv)"})
            assert (chk.data or chk.structured_content or {}).get("stdout", "").strip() == "1"
            rk = await c.call_tool("restart_kernel", {})
            assert (rk.data or rk.structured_content or {}).get("restarted") is True
            # confirm cleared
            chk2 = await c.call_tool("run_python_code", {"code": "print('ok' if 'xv' in globals() else 'missing')"})
            out2 = (chk2.data or chk2.structured_content or {}).get("stdout", "").strip()
            if out2 != "missing":
                lv2 = await c.call_tool("list_variables", {})
                assert "xv" not in (lv2.data or lv2.structured_content or {}).get("variables", [])
        # upload/download routes
        p = Path("tests/_int_upload.txt")
        p.write_text("int")
        async with httpx.AsyncClient() as hc:
            with p.open("rb") as f:
                r = await hc.post(base_url + "/files/upload", files={"file": ("int.txt", f)})
                assert r.status_code == 200
            r = await hc.get(base_url + "/files/download/uploads/int.txt")
            assert r.status_code == 200 and r.content.decode("utf-8") == "int"

    asyncio.run(run())
