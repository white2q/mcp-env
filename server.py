# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def summary(summaryHistory: str) -> str:
    """summary history"""
    return "当前会话历史记录：" + summaryHistory;

if __name__ == "__main__":
    mcp.run()
