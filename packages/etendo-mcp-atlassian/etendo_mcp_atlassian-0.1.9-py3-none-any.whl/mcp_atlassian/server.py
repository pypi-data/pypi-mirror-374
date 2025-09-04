# server.py
import sys
import asyncio
from mcp_atlassian.servers.main import build_server

def dump_tools_and_exit():
    """Dump available tools and exit - for debugging purposes."""
    srv = build_server(enable_network=False)
    
    # Get tools directly from mounted subservers to avoid context dependency
    async def get_tools():
        try:
            tools = []
            
            # Get tools from each mounted server
            all_mounted_tools = await srv.get_tools()
            for tool_name, tool_obj in all_mounted_tools.items():
                tools.append(tool_name)
            
            return tools
        except Exception as e:
            print(f"Error getting tools: {e}")
            return []
    
    names = asyncio.run(get_tools())
    print("TOOLS:", ", ".join(names))
    sys.exit(0)

def main():
    """Main entry point for the MCP server."""
    if "--dump-tools" in sys.argv:
        dump_tools_and_exit()

    # Build the server instance
    srv = build_server(enable_network=True)
    
    # Run the server using FastMCP's run method
    print("Starting Atlassian MCP server...")
    try:
        srv.run()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
