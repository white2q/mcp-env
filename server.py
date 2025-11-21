# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool(
    name="summary",
    description="总结会话历史记录，支持总结当前会话或全部会话历史，调用本工具时直接返回结果"
)
def summary(summaryHistory: str, historyType: str = "all") -> str:
    """summary history"""
    prefix = "全部会话历史记录：" if historyType == "all" else "当前会话历史记录："
    return prefix + summaryHistory

if __name__ == "__main__":
    mcp.run()