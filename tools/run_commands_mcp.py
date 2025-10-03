#!/usr/bin/env python3
"""
Compatible Run Commands MCP server:
 - creates initialization options for Server.run(...)
 - registers tools at runtime even when server.tool()/mcp.tool() aren't available
"""
import asyncio
import json
import os
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import inspect

import mcp
from mcp.server import Server

# Try importing stdio_server from the usual place(s)
try:
    from mcp.server.stdio import stdio_server
except Exception:
    try:
        # alternative fallback import names (rare)
        from mcp.server_stdio import stdio_server  # type: ignore
    except Exception:
        stdio_server = None  # we'll fail later with a clear message

server = Server("Run Commands MCP")

# Local registry used if decorators aren't available
_LOCAL_TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_tool(name: str | None = None):
    """
    Universal decorator factory:
     - prefer server.tool() if available
     - else prefer mcp.tool()
     - else store locally for manual registration
    """
    server_tool = getattr(server, "tool", None)
    module_tool = getattr(mcp, "tool", None)

    def _decorator(fn: Callable[..., Any]):
        tool_name = name or fn.__name__
        if callable(server_tool):
            # server.tool() likely returns a decorator
            return server_tool()(fn)
        if callable(module_tool):
            return module_tool()(fn)
        # fallback: keep locally for later manual registration
        _LOCAL_TOOL_REGISTRY[tool_name] = fn
        return fn

    return _decorator


def _clean_text(text: Optional[bytes]) -> Optional[str]:
    if text is None:
        return None
    return text.decode("utf-8", errors="backslashreplace").replace("\r\n", "\n")


async def _docker_exec(container_id: str, command: str, timeout: float) -> dict:
    proc = subprocess.Popen(
        ["docker", "exec", container_id, "bash", "-c", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return {
            "stdout": _clean_text(stdout),
            "stderr": _clean_text(stderr),
            "returncode": proc.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
        except Exception:
            pass
        stdout, stderr = proc.communicate()
        return {
            "stdout": _clean_text(stdout),
            "stderr": _clean_text(stderr),
            "returncode": None,
            "timed_out": True,
        }


@register_tool()
async def run_in_container(
    container_id: str,
    command: str,
    timeout: float = 10.0,
) -> str:
    if not container_id:
        return json.dumps({"error": "container_id is required"})
    if command is None:
        return json.dumps({"error": "command is required"})

    result = await _docker_exec(container_id, command, timeout)
    return json.dumps(result)


def _expand_user_path(path_str: str, home: Path) -> Path:
    if path_str.startswith("~"):
        path_str = path_str.replace("~", str(home), 1)
    return Path(path_str)


async def _copy_bytes_into_container(container_id: str, data: bytes, dest_path: Path) -> dict:
    try:
        subprocess.run(
            [
                "docker",
                "exec",
                container_id,
                "mkdir",
                "-p",
                str(dest_path.parent),
            ],
            check=False,
            capture_output=True,
        )
    except Exception as e:
        return {"error": f"mkdir in container failed: {e}"}

    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        tmp_path = tmp.name

    try:
        cp = subprocess.run(
            ["docker", "cp", "-aq", tmp_path, f"{container_id}:{dest_path}"],
            capture_output=True,
            text=True,
        )
        if cp.returncode != 0:
            return {
                "error": "docker cp failed",
                "stderr": cp.stderr,
                "stdout": cp.stdout,
                "returncode": cp.returncode,
            }
        return {"success": True, "path": str(dest_path)}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@register_tool()
async def create_file_in_container(
    container_id: str,
    path: str,
    contents: str,
    decode_escapes: bool = False,
    container_home: str = "/home/ctfplayer",
) -> str:
    if not container_id:
        return json.dumps({"error": "container_id is required"})
    if not path:
        return json.dumps({"error": "path is required"})
    if contents is None:
        return json.dumps({"error": "contents is required"})

    try:
        data = (
            bytes(contents, "utf-8").decode("unicode_escape").encode("latin-1")
            if decode_escapes
            else contents.encode()
        )
    except Exception as e:
        return json.dumps({"error": f"invalid contents encoding: {e}"})

    dest = Path(path)
    if not dest.is_absolute():
        dest = Path(container_home) / dest

    result = await _copy_bytes_into_container(container_id, data, dest)
    return json.dumps(result)


@register_tool()
async def list_running_containers() -> str:
    ps = subprocess.run(
        ["docker", "ps", "--format", "{{.ID}}\t{{.Names}}"],
        capture_output=True,
        text=True,
    )
    if ps.returncode != 0:
        return json.dumps({"error": ps.stderr.strip(), "returncode": ps.returncode})

    items = []
    for line in ps.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            items.append({"id": parts[0], "names": parts[1]})
    return json.dumps(items)


def _manual_register_local_tools():
    """
    Try to register stored local tools into the server with several fallbacks.
    """
    if not _LOCAL_TOOL_REGISTRY:
        return

    # 1) server.register_tool(name, fn) if exists
    if hasattr(server, "register_tool") and callable(getattr(server, "register_tool")):
        for name, fn in _LOCAL_TOOL_REGISTRY.items():
            try:
                server.register_tool(name, fn)
            except Exception:
                pass
        return

    # 2) inject into server._tool_cache (common internal)
    if hasattr(server, "_tool_cache") and isinstance(getattr(server, "_tool_cache"), dict):
        for name, fn in _LOCAL_TOOL_REGISTRY.items():
            server._tool_cache[name] = fn
        return

    # 3) module-level register function if present
    if hasattr(mcp, "register_tool") and callable(getattr(mcp, "register_tool")):
        for name, fn in _LOCAL_TOOL_REGISTRY.items():
            try:
                mcp.register_tool(name, fn)
            except Exception:
                pass
        return

    # 4) give a clear failure message and show available server attributes
    attrs = ", ".join(sorted(a for a in dir(server) if not a.startswith("_")))
    raise RuntimeError(
        "Couldn't auto-register tools: your 'mcp' package lacks server.tool/mcp.tool, "
        "and fallback registrations failed. Server attributes: " + attrs
    )


async def main() -> None:
    global stdio_server
    if stdio_server is None:
        try:
            from mcp.server.stdio import stdio_server as stdio_server  # type: ignore
        except Exception:
            pass

    # register stored tools in the best available way
    _manual_register_local_tools()

    # Create initialization options expected by server.run()
    try:
        init_opts = server.create_initialization_options()
    except Exception as e:
        print("ERROR creating initialization options:", e, file=sys.stderr)
        raise

    if stdio_server is None:
        print("ERROR: couldn't import stdio_server from mcp.server.stdio; check your mcp package", file=sys.stderr)
        raise SystemExit(1)

    async with stdio_server() as (read_stream, write_stream):
        # pass initialization options explicitly (some Server.run impls require it)
        await server.run(read_stream, write_stream, init_opts)


if __name__ == "__main__":
    asyncio.run(main())
