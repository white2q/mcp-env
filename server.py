# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name"""
    return "Hello " + name

if __name__ == "__main__":
    mcp.run()
