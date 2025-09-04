# server.py
import sys
from mcp.server.stdio import stdio_server
from mcp_atlassian.servers.main import build_server  # o como se llame tu factory

def dump_tools_and_exit():
    srv = build_server(enable_network=False)  # <— importante: que NO requiera Jira aquí
    tools = getattr(srv, "tools", None) or []
    names = [getattr(t, "name", repr(t)) for t in tools]
    print("TOOLS:", ", ".join(names))
    sys.exit(0)

def main():
    if "--dump-tools" in sys.argv:
        dump_tools_and_exit()

    # registra SIEMPRE las tools primero, sin tocar red
    srv = build_server(enable_network=False)

    # luego arrancás stdio; la red recién al invocar cada tool
    import asyncio
    async def run():
        async with stdio_server(srv) as s:
            await s.run()

    print("OK: starting main()")
    asyncio.run(run())
